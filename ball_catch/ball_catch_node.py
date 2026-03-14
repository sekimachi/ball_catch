from rclpy.node import Node
import rclpy
from std_msgs.msg import Bool
from std_msgs.msg import Bool

from imrc_messages.msg import GeneralCommand
from imrc_messages.msg import RobotActionProgress

class BallCatch(Node):

    def __init__(self):
        super().__init__('ball_catch')

        self.catch = False
        self.goal_handle = None

        # ===== Publisher =====
        self.back_pub = self.create_publisher(Bool, 'ball_back', 10)
        self.GC_pub = self.create_publisher(GeneralCommand,'robot_command',10)
        self.status_pub = self.create_publisher(Bool,'detect_ball_status',10)
        self.re_detect_pub = self.create_publisher(Bool,'re_detect',10)
        self.cali_ok_pub = self.create_publisher(Bool,'cali_ok',10)


        # ===== Subscriber =====
        self.create_subscription(Bool, 'ball_capture', self.capture_cb, 10)
        self.create_subscription(RobotActionProgress, 'robot_progress', self.progress_cb, 10)
        self.create_subscription(Bool, 'ball_cali', self.cali_cb, 10)
        

    def cali_cb(self, msg: Bool):
        self.GC_pub.publish(GeneralCommand(target="calibration", param=2)) #param=5はキャリブレーションする
        self.get_logger().info('キャリブレするように命令を送りました。')

    def capture_cb(self, msg: Bool):
        self.GC_pub.publish(GeneralCommand(target="ball", param=1)) #param=1はボールをキャッチする
        self.get_logger().info('ボールをキャッチするように命令を送りました。')

    # ===============================
    # robot_progressのコールバック。
    # ===============================
    def progress_cb(self, msg: RobotActionProgress):
        self.progress_msg = msg
        if msg.target == "ball" and msg.param == "catch"  and msg.state == "OK":
            self.get_logger().info('ボールをキャッチ完了')
            self.back_pub.publish(Bool(data=True)) #ボールをキャッチしたことを伝える

        elif msg.target == "ball" and msg.param == "catch"  and msg.state == "NG":
            self.get_logger().info('ボールをキャッチ失敗')
            self.re_detect_pub.publish(Bool(data=True))

        elif msg.target == "ball" and msg.param == "catch"  and msg.state == "Timeout":
            pass
        
        elif msg.target == "calibration" and msg.param == "arm" and msg.state == "OK":
            self.get_logger().info('キャリブレーション完了')
            self.cali_ok_pub.publish(Bool(data=True))


def main():
    rclpy.init()
    node = BallCatch()
    rclpy.spin(node)
    rclpy.shutdown()