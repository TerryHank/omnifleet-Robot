from test_missions import fleet

def test_temporary_navigation_not_ready_does_not_get_reported_as_offline(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':.4},fleet.states)
    fleet.tick(5)
    for r in ('a','b'):
        fleet.states[r]['transport_connected']=True
        fleet.states[r]['samples']['navigation']['value']['local_ready']=False
        fleet.states[r]['fresh']['pose']=False
        fleet.states[r]['online']=False
    fleet.maps.valid_robots.clear()
    fleet.tick(3)
    assert fleet.owner.follow['active']
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'
    assert any(p[0]=='follow_update' for p in fleet.sent)
    assert not any(p[0]=='disarm' for p in fleet.sent)

def test_actual_transport_loss_is_still_reported_by_vehicle_name(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':.4},fleet.states)
    fleet.tick(5);fleet.states['b']['transport_connected']=False;fleet.tick()
    assert not fleet.owner.follow['active']
    assert 'b：接入连接中断' in fleet.owner.follow['message']
