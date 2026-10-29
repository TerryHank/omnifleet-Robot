# WSL central workspace

- Source: `src/<functional-domain>/<package>`. Package configuration: package `config/`.
- Runtime state, RMF database and evidence: `data/`. Build products: `build/`, `install/`, `log/`.
- Central RMF control and independent onboard leases are authorized. Use local_navigation FLEET API, never impersonate MSC messages or bypass its safety output. Live motion acceptance is bounded to the explicitly agreed range and on-site conditions.
- Central ROS domain 42 uses native Zenoh through the WSL loopback router. Robot 104 uses verified domain 104 and native Zenoh. Robot 113 stays disabled until its effective domain and middleware are verified.
- Keep ROS domains in separate processes. Exchange only compact state over local Unix sockets.
- Target vehicle interfaces and TF are local, without vehicle prefixes. Central `assignments` owns the exported namespace and RMF name. `observed_namespace` is a temporary explicit compatibility setting for the current vehicle runtime, not the target architecture.
- Do not register a robot as schedulable until its map transform, navigation graph, path timing, lease expiry and stop behavior have been validated.
- Preserve current vehicle configuration and rollback material. Do not copy the robot 113 configuration onto robot 104.
