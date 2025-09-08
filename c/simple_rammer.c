#include "math.h"
#include "bot.h"

Config config;

void init(Config cfg) {
    setColor(1.0, 0.0, 0.0);
    config = cfg;
}

void update(State state) {
    float xDiff = state.enemyXPos - state.xPos;
    float yDiff = state.enemyYPos - state.yPos;

    if(xDiff == 0 && yDiff == 0)
        return;

    float mag = sqrt(xDiff * xDiff + yDiff * yDiff);
    
    sendAction((xDiff / mag) * config.maxPuckAccel, (yDiff / mag) * config.maxPuckAccel);
}