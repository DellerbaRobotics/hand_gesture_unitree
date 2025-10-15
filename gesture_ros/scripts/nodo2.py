#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from geometry_msgs.msg import Twist


#dividere i due nodi
class GestureSubscriber:
    def __init__(self):
        rospy.init_node('gesture_subscriber_node', anonymous=True)
        self.bridge = CvBridge()
        rospy.Subscriber('recognized_gesture', String, self.gesture_callback)
        rospy.Subscriber('gesture_image', Image, self.image_callback)
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.last_gesture = "Empty"
        rospy.loginfo("Nodo subscriber gesture avviato.")

    def gesture_callback(self, msg):
        self.last_gesture = msg.data
        rospy.loginfo(f"Gesto ricevuto: {self.last_gesture}")
        twist = Twist()
        if self.last_gesture == "ThumbU":
            rospy.loginfo("Avanza")
            twist.linear.x = 0.5
            twist.angular.z = 0.0
        elif self.last_gesture == "ThumbD":
            rospy.loginfo("Indietro")
            twist.linear.x = -0.5
            twist.angular.z = 0.0
        elif self.last_gesture == "HandOpen":
            rospy.loginfo("Stop")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif self.last_gesture == "Point":
            rospy.loginfo("Start")
            twist.linear.x = 0.5
            twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            cv2.imshow("Gesture Annotata", frame)
            cv2.waitKey(1)
        except Exception as e:
            rospy.logerr(f"Errore nella conversione immagine: {e}")

    def spin(self):
        rospy.spin()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        gs = GestureSubscriber()
        gs.spin()
    except rospy.ROSInterruptException:
        pass
