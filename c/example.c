
// compile: clang --target=wasm32 -nostdlib -Wall,--no-entry -Wl,--export=add -o out.wasm example.c

#include <stdlib.h>
#include "bot.h"


void init() {
}

void update() {
  sendActions(ACTION_RIGHT | ACTION_THRUST);
}