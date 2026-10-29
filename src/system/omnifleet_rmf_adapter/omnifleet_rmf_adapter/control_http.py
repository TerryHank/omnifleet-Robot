"""Loopback UI API. The ROS executor owns all commands and task state."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json,queue,secrets,threading

class ControlHTTP:
    def __init__(self):
        self.inbox=queue.Queue();self.token=secrets.token_urlsafe(32);self.state={'ready':False}
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def allowed(self):return self.headers.get('Origin') in (None,'null','http://localhost:3000','http://127.0.0.1:3000','http://localhost:8080','http://127.0.0.1:8080')
            def reply(self,code,payload):
                data=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode()
                self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin',self.headers.get('Origin','null'))
                self.send_header('Access-Control-Allow-Headers','Content-Type,X-OmniFleet-Token')
                self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS');self.end_headers();self.wfile.write(data)
            def do_OPTIONS(self):self.reply(200,{}) if self.allowed() else self.reply(403,{'error':'origin not allowed'})
            def do_GET(self):
                if not self.allowed():self.reply(403,{'error':'origin not allowed'});return
                if self.path!='/state':self.reply(404,{});return
                self.reply(200,{**owner.state,'token':owner.token})
            def do_POST(self):
                if not self.allowed() or self.headers.get('X-OmniFleet-Token')!=owner.token:
                    self.reply(403,{'error':'session required'});return
                size=int(self.headers.get('Content-Length',0))
                if self.path!='/command' or not 0<size<=16384:self.reply(400,{});return
                try:
                    packet=json.loads(self.rfile.read(size))
                    if packet.get('op') not in ('dispatch_goal','dispatch_stop','rmf_submit_task','shared_costmap_configure','dispatch_order','traffic_configure','traffic_recover','traffic_call','dispatch_settings','web_goal','web_manual','web_stop','web_estimate','web_watch','web_diagnostic','web_service','nav_parameters_read','nav_parameters_save','follow_start','follow_stop','formation_capture','formation_start','formation_stop','route_save','route_update','route_clear','routes_clear','route_prepare','route_start','route_stop','routes_start','routes_stop','align_maps','robot_rename','robot_reassign','execution_permission') or not isinstance(packet.get('id'),str) or not 1<=len(packet['id'])<=160:raise ValueError('invalid command')
                    owner.inbox.put(packet);self.reply(202,{'request_id':packet['id'],'queued':True})
                except ValueError as error:self.reply(400,{'error':str(error)})
        self.server=ThreadingHTTPServer(('127.0.0.1',8081),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
