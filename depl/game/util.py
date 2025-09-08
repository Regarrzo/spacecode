
def raycast(origin: complex, direction: complex, l1: complex, l2: complex):
    '''
    Casts a ray originating from origin in direction, computing the intersection of the ray and the line spanned by l1 and l2.
    Returns the intersection point as a complex number if it exists on the ray, otherwise None.
    '''

    line_dir = l2 - l1

    det = (direction.real * -line_dir.imag) - (direction.imag * -line_dir.real)

    if abs(det) < 1e-12:
        return None

    rhs = l1 - origin

    t = (rhs.real * -line_dir.imag - rhs.imag * -line_dir.real) / det

    if t < 0:
        return None

    return origin + t * direction
