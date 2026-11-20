#include <fastcdr/Cdr.h>
#include <fastcdr/FastBuffer.h>
#include <fastdds/dds/domain/DomainParticipant.hpp>
#include <fastdds/dds/domain/DomainParticipantFactory.hpp>
#include <fastdds/dds/publisher/DataWriter.hpp>
#include <fastdds/dds/publisher/Publisher.hpp>
#include <fastdds/dds/subscriber/DataReader.hpp>
#include <fastdds/dds/subscriber/SampleInfo.hpp>
#include <fastdds/dds/subscriber/Subscriber.hpp>
#include <fastdds/dds/topic/TypeSupport.hpp>
#include <fastdds/rtps/transport/UDPv4TransportDescriptor.h>
#include <fastrtps/utils/IPLocator.h>

#include <cstring>
#include <memory>
#include <string>
#include <vector>

#ifdef __ANDROID__
#include <jni.h>
#endif

using namespace eprosima::fastdds::dds;
using namespace eprosima::fastrtps::rtps;
using eprosima::fastrtps::types::ReturnCode_t;
using eprosima::fastcdr::Cdr;
using eprosima::fastcdr::FastBuffer;

namespace {
constexpr uint32_t max_video = 192 * 1024;
constexpr uint32_t max_overlay = 12 * 1024;
constexpr unsigned domain = 106;
constexpr unsigned car_discovery = 17650;
constexpr unsigned g20_discovery = 17652;
constexpr const char* topic_name = "omnifleet/follow/h264";

struct Frame {
    uint64_t stamp = 0;
    uint32_t sequence = 0;
    uint32_t keyframe = 0;
    std::vector<uint8_t> video;
    std::string overlay;
};

class FrameType : public TopicDataType {
public:
    FrameType() {
        setName("omnifleet::FollowH264Frame");
        m_typeSize = max_video + max_overlay + 64;
        m_isGetKeyDefined = false;
        auto_fill_type_object(false);
        auto_fill_type_information(false);
    }

    bool serialize(void* data, SerializedPayload_t* payload) override {
        const auto& frame = *static_cast<Frame*>(data);
        try {
            FastBuffer buffer(reinterpret_cast<char*>(payload->data), payload->max_size);
            Cdr cdr(buffer, Cdr::DEFAULT_ENDIAN, Cdr::DDS_CDR);
            payload->encapsulation = cdr.endianness() == Cdr::BIG_ENDIANNESS ? CDR_BE : CDR_LE;
            cdr.serialize_encapsulation();
            cdr << frame.stamp << frame.sequence << frame.keyframe;
            cdr << static_cast<uint32_t>(frame.video.size()) << static_cast<uint32_t>(frame.overlay.size());
            cdr.serializeArray(frame.video.data(), frame.video.size());
            cdr.serializeArray(frame.overlay.data(), frame.overlay.size());
            payload->length = static_cast<uint32_t>(cdr.getSerializedDataLength());
            return true;
        } catch (const std::exception&) {
            return false;
        }
    }

    bool deserialize(SerializedPayload_t* payload, void* data) override {
        auto& frame = *static_cast<Frame*>(data);
        try {
            FastBuffer buffer(reinterpret_cast<char*>(payload->data), payload->length);
            Cdr cdr(buffer, Cdr::DEFAULT_ENDIAN, Cdr::DDS_CDR);
            cdr.read_encapsulation();
            uint32_t video_size, overlay_size;
            cdr >> frame.stamp >> frame.sequence >> frame.keyframe >> video_size >> overlay_size;
            if (video_size == 0 || video_size > max_video || overlay_size > max_overlay) return false;
            frame.video.resize(video_size);
            frame.overlay.resize(overlay_size);
            cdr.deserializeArray(frame.video.data(), video_size);
            cdr.deserializeArray(frame.overlay.data(), overlay_size);
            return true;
        } catch (const std::exception&) {
            return false;
        }
    }

    std::function<uint32_t()> getSerializedSizeProvider(void* data) override {
        return [data] {
            const auto& frame = *static_cast<Frame*>(data);
            return static_cast<uint32_t>(28 + frame.video.size() + frame.overlay.size());
        };
    }

    void* createData() override { return new Frame(); }
    void deleteData(void* data) override { delete static_cast<Frame*>(data); }
    bool getKey(void*, InstanceHandle_t*, bool) override { return false; }
};

struct Endpoint {
    TypeSupport type{new FrameType};
    DomainParticipant* participant = nullptr;
    DataWriter* writer = nullptr;
    DataReader* reader = nullptr;
    Frame frame;

    ~Endpoint() {
        if (participant) {
            participant->delete_contained_entities();
            DomainParticipantFactory::get_instance()->delete_participant(participant);
        }
    }
};

Locator_t ipv4(const char* address, unsigned port) {
    Locator_t locator;
    locator.kind = LOCATOR_KIND_UDPv4;
    locator.port = port;
    IPLocator::setIPv4(locator, address);
    return locator;
}

template<class Qos> void media_qos(Qos& qos) {
    qos.data_sharing().off();
    qos.history().kind = KEEP_LAST_HISTORY_QOS;
    qos.history().depth = 6;
    qos.resource_limits().max_instances = 1;
    qos.resource_limits().max_samples = 8;
    qos.resource_limits().max_samples_per_instance = 8;
    qos.resource_limits().allocated_samples = 6;
    qos.reliability().kind = BEST_EFFORT_RELIABILITY_QOS;
    qos.endpoint().history_memory_policy = PREALLOCATED_WITH_REALLOC_MEMORY_MODE;
}
}  // namespace

extern "C" void* media_open(const char* local, const char* peer, bool publishing) {
    auto endpoint = std::make_unique<Endpoint>();
    DomainParticipantQos qos;
    qos.name(publishing ? "124_h264_gr01" : "g20_h264_gr01");
    auto udp = std::make_shared<eprosima::fastdds::rtps::UDPv4TransportDescriptor>();
    udp->interfaceWhiteList.push_back(local);
    udp->maxMessageSize = 1380;
    udp->sendBufferSize = 256 * 1024;
    udp->receiveBufferSize = 512 * 1024;
    qos.transport().use_builtin_transports = false;
    qos.transport().user_transports.push_back(udp);
    unsigned own_port = publishing ? car_discovery : g20_discovery;
    unsigned peer_port = publishing ? g20_discovery : car_discovery;
    auto& wire = qos.wire_protocol();
    wire.builtin.metatrafficUnicastLocatorList.push_back(ipv4(local, own_port));
    wire.builtin.initialPeersList.push_back(ipv4(peer, peer_port));
    wire.default_unicast_locator_list.push_back(ipv4(local, own_port + 1));
    endpoint->participant = DomainParticipantFactory::get_instance()->create_participant(domain, qos);
    if (!endpoint->participant || endpoint->type.register_type(endpoint->participant) != ReturnCode_t::RETCODE_OK)
        return nullptr;
    auto topic = endpoint->participant->create_topic(topic_name, endpoint->type.get_type_name(), TOPIC_QOS_DEFAULT);
    if (!topic) return nullptr;
    if (publishing) {
        Publisher* publisher = endpoint->participant->create_publisher(PUBLISHER_QOS_DEFAULT);
        DataWriterQos writer_qos;
        media_qos(writer_qos);
        if (!publisher || !(endpoint->writer = publisher->create_datawriter(topic, writer_qos))) return nullptr;
    } else {
        Subscriber* subscriber = endpoint->participant->create_subscriber(SUBSCRIBER_QOS_DEFAULT);
        DataReaderQos reader_qos;
        media_qos(reader_qos);
        if (!subscriber || !(endpoint->reader = subscriber->create_datareader(topic, reader_qos))) return nullptr;
    }
    return endpoint.release();
}

extern "C" int media_matched(void* handle) {
    auto& endpoint = *static_cast<Endpoint*>(handle);
    PublicationMatchedStatus status;
    endpoint.writer->get_publication_matched_status(status);
    return status.current_count;
}

extern "C" bool media_write(void* handle, uint64_t stamp, uint32_t sequence, bool keyframe,
                            const uint8_t* video, uint32_t size, const char* overlay, uint32_t overlay_size) {
    if (size == 0 || size > max_video || overlay_size > max_overlay) return false;
    auto& endpoint = *static_cast<Endpoint*>(handle);
    auto& frame = endpoint.frame;
    frame.stamp = stamp;
    frame.sequence = sequence;
    frame.keyframe = keyframe;
    frame.video.assign(video, video + size);
    frame.overlay.assign(overlay, overlay_size);
    return endpoint.writer->write(&frame, HANDLE_NIL) == ReturnCode_t::RETCODE_OK;
}

extern "C" void media_close(void* handle) { delete static_cast<Endpoint*>(handle); }

#ifdef __ANDROID__
extern "C" JNIEXPORT jlong JNICALL
Java_dev_terryhank_foxglove_cn_FollowMedia_open(JNIEnv*, jclass) {
    return reinterpret_cast<jlong>(media_open("192.168.144.11", "192.168.144.108", false));
}

extern "C" JNIEXPORT jint JNICALL
Java_dev_terryhank_foxglove_cn_FollowMedia_take(JNIEnv* env, jclass, jlong handle,
        jobject video, jbyteArray overlay, jlongArray header) {
    auto& endpoint = *reinterpret_cast<Endpoint*>(handle);
    auto& frame = endpoint.frame;
    SampleInfo info;
    auto result = endpoint.reader->take_next_sample(&frame, &info);
    if (result == ReturnCode_t::RETCODE_NO_DATA) return 0;
    if (result != ReturnCode_t::RETCODE_OK || !info.valid_data) return -1;
    if (env->GetDirectBufferCapacity(video) < static_cast<jlong>(frame.video.size()) ||
        env->GetArrayLength(overlay) < static_cast<jsize>(frame.overlay.size())) return -1;
    std::memcpy(env->GetDirectBufferAddress(video), frame.video.data(), frame.video.size());
    env->SetByteArrayRegion(overlay, 0, static_cast<jsize>(frame.overlay.size()),
                           reinterpret_cast<const jbyte*>(frame.overlay.data()));
    jlong fields[] = {static_cast<jlong>(frame.stamp), frame.sequence, frame.keyframe,
                      static_cast<jlong>(frame.overlay.size())};
    env->SetLongArrayRegion(header, 0, 4, fields);
    return static_cast<jint>(frame.video.size());
}

extern "C" JNIEXPORT void JNICALL
Java_dev_terryhank_foxglove_cn_FollowMedia_close(JNIEnv*, jclass, jlong handle) {
    media_close(reinterpret_cast<void*>(handle));
}
#endif
