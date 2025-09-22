




__attribute__((import_name("set_color")))
/**
 * @brief Sets the color of your puck. All values should be between 0 and 1.
 * @details 
 */
void setColor(float r, float g, float b);



__attribute__((export_name("update")))
void _update(float xPos, float yPos, float xVel, float yVel, float enemyXPos, float enemyYPos, float enemyXVel, float enemyYVel) {
    State state = { xPos, yPos, xVel, yVel, enemyXPos, enemyYPos, enemyXVel, enemyYVel };
    update(state);
}

