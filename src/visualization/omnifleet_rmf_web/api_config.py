from api_server.default_config import config

config = dict(config)
config.update(
    host="127.0.0.1",
    port=8000,
    public_url="http://localhost:8000",
    db_url="sqlite:///home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/db.sqlite3",
    cache_directory="/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/cache",
    ros_args=["-p", "use_sim_time:=false"],
    log_level="INFO",
)
