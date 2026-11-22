// Copyright (c) 2022 Samsung Research America, @artofnothingness Alexey Budyakov
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef NAV2_MPPI_CONTROLLER__MOTION_MODELS_HPP_
#define NAV2_MPPI_CONTROLLER__MOTION_MODELS_HPP_

#include <cstdint>
#include <algorithm>
#include <cmath>
#include <limits>
#include <string>
#include <utility>

#include "nav2_mppi_controller/models/control_sequence.hpp"
#include "nav2_mppi_controller/models/state.hpp"
#include <xtensor/xmath.hpp>
#include <xtensor/xmasked_view.hpp>
#include <xtensor/xview.hpp>
#include <xtensor/xnoalias.hpp>

#include "nav2_mppi_controller/tools/parameters_handler.hpp"

namespace mppi
{

/**
 * @class mppi::MotionModel
 * @brief Abstract motion model for modeling a vehicle
 */
class MotionModel
{
public:
  /**
    * @brief Constructor for mppi::MotionModel
    */
  MotionModel() = default;

  void initializeAcceleration(ParametersHandler * param_handler, const std::string & name)
  {
    auto getParam = param_handler->getParamGetter(name);
    getParam(angular_acceleration_, "az_max", 3.5f);
    getParam(linear_acceleration_, "ax_max", 3.0f);
    getParam(linear_deceleration_, "ax_min", -3.0f);
  }

  void constrainVelocityChange(float current_v, float current_w,
    float & target_v, float & target_w, float dt) const
  {
    const float dv = target_v-current_v, dw = target_w-current_w;
    float scale = 1.f;
    if (dv != 0.f) {
      const float limit = dv > 0.f ? linear_acceleration_ : linear_deceleration_;
      scale = std::min(scale, std::abs(limit)*dt/std::abs(dv));
    }
    if (dw != 0.f) {
      scale = std::min(scale, std::abs(angular_acceleration_)*dt/std::abs(dw));
    }
    target_v = current_v+scale*dv;
    target_w = current_w+scale*dw;
  }

  std::pair<float, float> commandReference(float measured_v, float measured_w) const
  {return have_command_ ? std::make_pair(command_v_, command_w_) :
           std::make_pair(measured_v, measured_w);}

  void rememberCommand(float v, float w)
  {command_v_ = v; command_w_ = w; have_command_ = true;}

  void resetCommand() {have_command_ = false;}

  void applyAcceleration(models::State & state, float dt) const
  {
    for (size_t i = 0; i < state.cwz.shape(0); ++i) {
      float actual_v = state.vx(i, 0), actual_w = state.wz(i, 0);
      auto [command_v, command_w] = commandReference(actual_v, actual_w);
      for (size_t j = 0; j < state.cwz.shape(1); ++j) {
        float v = state.cvx(i, j), w = state.cwz(i, j);
        constrainVelocityChange(command_v, command_w, v, w, dt);
        state.cvx(i, j) = command_v = v;
        state.cwz(i, j) = command_w = w;
        // Commands progress from the previous command; physical prediction
        // starts at measured velocity even when feedback arrives more slowly.
        constrainVelocityChange(actual_v, actual_w, v, w, dt);
        actual_v = v; actual_w = w;
        if (j + 1 < state.wz.shape(1)) {
          state.vx(i, j + 1) = actual_v; state.wz(i, j + 1) = actual_w;
        }
      }
    }
  }

  /**
    * @brief Destructor for mppi::MotionModel
    */
  virtual ~MotionModel() = default;

  /**
   * @brief With input velocities, find the vehicle's output velocities
   * @param state Contains control velocities to use to populate vehicle velocities
   */
  virtual void predict(models::State & state)
  {
    using namespace xt::placeholders;  // NOLINT
    xt::noalias(xt::view(state.vx, xt::all(), xt::range(1, _))) =
      xt::view(state.cvx, xt::all(), xt::range(0, -1));

    xt::noalias(xt::view(state.wz, xt::all(), xt::range(1, _))) =
      xt::view(state.cwz, xt::all(), xt::range(0, -1));

    if (isHolonomic()) {
      xt::noalias(xt::view(state.vy, xt::all(), xt::range(1, _))) =
        xt::view(state.cvy, xt::all(), xt::range(0, -1));
    }
  }

  /**
   * @brief Whether the motion model is holonomic, using Y axis
   * @return Bool If holonomic
   */
  virtual bool isHolonomic() = 0;

  /**
   * @brief Apply hard vehicle constraints to a control sequence
   * @param control_sequence Control sequence to apply constraints to
   */
  virtual void applyConstraints(models::ControlSequence & /*control_sequence*/) {}

private:
  float angular_acceleration_{std::numeric_limits<float>::max()};
  float linear_acceleration_{std::numeric_limits<float>::max()};
  float linear_deceleration_{std::numeric_limits<float>::max()};
  float command_v_{0.f}, command_w_{0.f};
  bool have_command_{false};
};

/**
 * @class mppi::AckermannMotionModel
 * @brief Ackermann motion model
 */
class AckermannMotionModel : public MotionModel
{
public:
  /**
    * @brief Constructor for mppi::AckermannMotionModel
    */
  explicit AckermannMotionModel(ParametersHandler * param_handler, const std::string & name)
  {
    auto getParam = param_handler->getParamGetter(name + ".AckermannConstraints");
    getParam(min_turning_r_, "min_turning_r", 0.2);
  }

  /**
   * @brief Whether the motion model is holonomic, using Y axis
   * @return Bool If holonomic
   */
  bool isHolonomic() override
  {
    return false;
  }

  /**
   * @brief Apply hard vehicle constraints to a control sequence
   * @param control_sequence Control sequence to apply constraints to
   */
  void applyConstraints(models::ControlSequence & control_sequence) override
  {
    auto & vx = control_sequence.vx;
    auto & wz = control_sequence.wz;

    auto view = xt::masked_view(wz, (xt::fabs(vx) / xt::fabs(wz)) < min_turning_r_);
    view = xt::sign(wz) * xt::fabs(vx) / min_turning_r_;
  }

  /**
   * @brief Get minimum turning radius of ackermann drive
   * @return Minimum turning radius
   */
  float getMinTurningRadius() {return min_turning_r_;}

private:
  float min_turning_r_{0};
};

/**
 * @class mppi::DiffDriveMotionModel
 * @brief Differential drive motion model
 */
class DiffDriveMotionModel : public MotionModel
{
public:
  /**
    * @brief Constructor for mppi::DiffDriveMotionModel
    */
  DiffDriveMotionModel() = default;

  /**
   * @brief Whether the motion model is holonomic, using Y axis
   * @return Bool If holonomic
   */
  bool isHolonomic() override
  {
    return false;
  }
};

/**
 * @class mppi::OmniMotionModel
 * @brief Omnidirectional motion model
 */
class OmniMotionModel : public MotionModel
{
public:
  /**
    * @brief Constructor for mppi::OmniMotionModel
    */
  OmniMotionModel() = default;

  /**
   * @brief Whether the motion model is holonomic, using Y axis
   * @return Bool If holonomic
   */
  bool isHolonomic() override
  {
    return true;
  }
};

}  // namespace mppi

#endif  // NAV2_MPPI_CONTROLLER__MOTION_MODELS_HPP_
