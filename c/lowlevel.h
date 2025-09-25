#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

char* _lowlevel_outgoing_message_buffer = NULL;
char* _lowlevel_incoming_message_buffer = NULL;

/*
INCOMING MESSAGE PROTOCOL:
HOST: calls _lowlevel_prepare_incoming_message_buffer
CLIENT: char* to a suitable location is provided
HOST: copies message to the char*
*/

__attribute__((export_name("prepare_incoming_message")))
char* _lowlevel_prepare_incoming_message_buffer(size_t requested_size) {
    /// Called by the host to request memory to send a message to WASM
    free(_lowlevel_incoming_message_buffer);
    _lowlevel_incoming_message_buffer = (char*) malloc(requested_size * sizeof(char));
    return _lowlevel_incoming_message_buffer;
}

__attribute__((export_name("notify_message_ready")))
void _lowlevel_notify_incoming_message(char* ptr, size_t message_size) {
    /// Called by the host as soon as copying is finished. ptr should match up with _lowlevel_incoming_message_buffer
    printf(ptr);
}

__attribute__((export_name("get_outgoing_message")))
char* _lowlevel_provide_message() {
    /// Called by the host to read the message prepared by the client. Must be null terminated.
    return _lowlevel_outgoing_message_buffer;
}