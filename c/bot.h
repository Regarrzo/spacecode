#pragma once

// ### USER IMPLEMENTED FUNCTIONS ###
__attribute__((export_name("init")))
/**
 * @brief Called at the beginning of every match
 * @details This might contain some stuff like initial position, enemy count, 
 */
void init();

__attribute__((export_name("update")))
/**
 * @brief Called before every tick. You should call sendActions in here to set your next move.
 * @details 
 */
void update();


// ### LIBRARY FUNCTIONS AND DEFINITIONS ###
#define ACTION_THRUST   0b001
#define ACTION_LEFT     0b010
#define ACTION_RIGHT    0b100

__attribute__((import_name("send_actions")))
/**
 * @brief Sends control actions to the host environment.
 * @details This only needs to be sent once per tick. Only the latest sent actions are executed
 * at the end of the tick.
 * @param actionFlags A bitmask of actions to perform. Can be a combination of
 *                    ACTION_THRUST, ACTION_LEFT, and ACTION_RIGHT.
 */
void sendActions(int actionFlags);

