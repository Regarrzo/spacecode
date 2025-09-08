#pragma once

__attribute__((import_name("send_action")))
/**
 * @brief Send an action to the host. Only the most recently sent action will be executed at the end of the tick.
 * @details 
 */
void sendAction(float x_accel, float y_accel);

typedef struct Config {
    float boundaryRadius;
    float puckRadius;
    float maxPuckAccel;
    float damping;
} Config;

typedef struct State {
    float xPos, yPos, xVel, yVel;
    float enemyXPos, enemyYPos, enemyXVel, enemyYVel;
} State;

/**
 * @brief Called at the beginning of every match
 * @details This might contain some stuff like initial position, enemy count, 
 */
void init(Config cfg);

/**
 * @brief Called before every tick. You should call sendAction in here to set your next move.
 * @details 
 */
void update(State state);


__attribute__((export_name("init")))
void _init(float boundaryRadius, float puckRadius, float maxPuckAccel, float damping) {
    Config cfg = {boundaryRadius, puckRadius, maxPuckAccel, damping};
    init(cfg);
}

__attribute__((export_name("update")))
void _update(float xPos, float yPos, float xVel, float yVel, float enemyXPos, float enemyYPos, float enemyXVel, float enemyYVel) {
    State state = { xPos, yPos, xVel, yVel, enemyXPos, enemyYPos, enemyXVel, enemyYVel };
    update(state);
}