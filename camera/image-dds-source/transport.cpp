#include "ImageFramePubSubTypes.h"
#include <fastdds/dds/domain/DomainParticipantFactory.hpp>
#include <fastdds/dds/domain/DomainParticipant.hpp>
#include <fastdds/dds/topic/TypeSupport.hpp>
#include <fastdds/dds/publisher/Publisher.hpp>
#include <fastdds/dds/publisher/DataWriter.hpp>
#include <fastdds/dds/subscriber/Subscriber.hpp>
#include <fastdds/dds/subscriber/DataReader.hpp>
#include <fastdds/dds/core/LoanableSequence.hpp>
#include <fastdds/rtps/transport/UDPv4TransportDescriptor.h>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <memory>
#include <string>

using namespace eprosima::fastdds::dds;
using eprosima::fastrtps::types::ReturnCode_t;

namespace {
struct Endpoint {
    TypeSupport type{new ImageFramePubSubType};
    DomainParticipant* participant = nullptr;
    DataWriter* writer = nullptr;
    DataReader* reader = nullptr;
    unsigned counter = 0;
    ~Endpoint() {
        if (participant) {
            participant->delete_contained_entities();
            DomainParticipantFactory::get_instance()->delete_participant(participant);
        }
    }
};

void report(const char* side, const ImageFrame& frame) {
    if (frame.reserved() % 60 != 0) return;
    auto address = reinterpret_cast<uintptr_t>(frame.pixels().data());
    std::ifstream maps("/proc/self/maps");
    std::string line;
    while (std::getline(maps,line)) {
        unsigned long start,end,offset,inode;
        char device[20], perms[5];
        if (std::sscanf(line.c_str(),"%lx-%lx %4s %lx %19s %lu",&start,&end,perms,&offset,device,&inode)!=6 ||
            address<start || address>=end) continue;
        std::fprintf(stderr,"image_loan %s frame=%u stamp=%llu bytes=%u backing=%s:%lu offset=%lu shared=%c\n",
            side, frame.reserved(), static_cast<unsigned long long>(frame.capture_ns()),frame.length(),
            device,inode,offset+address-start,perms[3]);
        break;
    }
}

template<class Qos> void configure(Qos& qos) {
    qos.data_sharing().on("");
    qos.history().depth = 3;
    qos.resource_limits().max_instances = 1;
    qos.resource_limits().allocated_samples = 5;
    qos.resource_limits().max_samples = qos.resource_limits().max_samples_per_instance = 8;
    qos.reliability().kind = RELIABLE_RELIABILITY_QOS;
    qos.endpoint().history_memory_policy = eprosima::fastrtps::rtps::PREALLOCATED_MEMORY_MODE;
}
}

extern "C" void* image_open(unsigned domain, const char* name, bool publishing) {
    auto ep = std::make_unique<Endpoint>();
    DomainParticipantQos qos;
    qos.name(publishing ? "omnifleet_image_writer" : "omnifleet_image_reader");
    auto udp = std::make_shared<eprosima::fastdds::rtps::UDPv4TransportDescriptor>();
    udp->interfaceWhiteList.push_back("127.0.0.1");
    qos.transport().use_builtin_transports = false;
    qos.transport().user_transports.push_back(udp);
    ep->participant = DomainParticipantFactory::get_instance()->create_participant(domain,qos);
    if (!ep->participant || ep->type.register_type(ep->participant)!=ReturnCode_t::RETCODE_OK) return nullptr;
    auto topic = ep->participant->create_topic(name,ep->type.get_type_name(),TOPIC_QOS_DEFAULT);
    if (!topic) return nullptr;
    if (publishing) {
        auto pub = ep->participant->create_publisher(PUBLISHER_QOS_DEFAULT);
        DataWriterQos wq;
        configure(wq);
        if (!pub || !(ep->writer=pub->create_datawriter(topic,wq))) return nullptr;
    } else {
        auto sub = ep->participant->create_subscriber(SUBSCRIBER_QOS_DEFAULT);
        DataReaderQos rq;
        configure(rq);
        if (!sub || !(ep->reader=sub->create_datareader(topic,rq))) return nullptr;
    }
    return ep.release();
}

extern "C" bool image_publish(void* endpoint, const void* input, unsigned size, uint64_t stamp) {
    if (!input || !size || size>1048576) return false;
    auto& ep = *static_cast<Endpoint*>(endpoint);
    void* loan = nullptr;
    if (ep.writer->loan_sample(loan)!=ReturnCode_t::RETCODE_OK) return false;
    auto& frame = *static_cast<ImageFrame*>(loan);
    frame.capture_ns(stamp);
    frame.reserved(++ep.counter);
    frame.length(size);
    std::memcpy(frame.pixels().data(), input, size);
    report("write",frame);
    if (ep.writer->write(loan,HANDLE_NIL)==ReturnCode_t::RETCODE_OK) return true;
    ep.writer->discard_loan(loan);
    return false;
}

using FrameCallback = void(*)(const uint8_t*, unsigned, uint64_t);
extern "C" int image_take(void* endpoint, FrameCallback consume) {
    auto& ep = *static_cast<Endpoint*>(endpoint);
    LoanableSequence<ImageFrame> frames;
    SampleInfoSeq infos;
    auto status = ep.reader->take(frames,infos,1);
    if (status==ReturnCode_t::RETCODE_NO_DATA) return 0;
    if (status!=ReturnCode_t::RETCODE_OK) return -1;
    if (infos[0].valid_data && ep.reader->is_sample_valid(&frames[0],&infos[0])
        && frames[0].length()<=frames[0].pixels().size()) {
        const auto& frame=frames[0];
        report("read",frame);
        consume(frame.pixels().data(),frame.length(),frame.capture_ns());
    }
    return ep.reader->return_loan(frames,infos)==ReturnCode_t::RETCODE_OK ? 1 : -1;
}

extern "C" void image_close(void* endpoint) { delete static_cast<Endpoint*>(endpoint); }
