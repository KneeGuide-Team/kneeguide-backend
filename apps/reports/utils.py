def analyze_motion(motion_data, normal_angle):
    if not motion_data:
        return 0, normal_angle, normal_angle, "poor", 0

    # أعلى زاوية
    max_angle = max(point["angle"] for point in motion_data)

    # الفرق عن الطبيعي
    deviation = abs(normal_angle - max_angle)

    # الأداء
    if max_angle >= normal_angle:
        status = "excellent"
    elif max_angle >= normal_angle * 0.75:
        status = "good"
    else:
        status = "poor"

    # الزمن
    duration = motion_data[-1].get("time", 0)

    return max_angle, deviation, normal_angle, status, duration
