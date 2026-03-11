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

        # ===== Subscriber =====
        self.create_subscription(Bool, 'ball_capture', self.capture_cb, 10)
        self.create_subscription(RobotActionProgress, 'robot_progress', self.progress_cb, 10)
        self.create_subscription(Bool, 'tanav2_position', self.tanav2_position_cb, 10)
        
        

    def capture_cb(self, msg: Bool):
        self.GC_pub.publish(GeneralCommand(target="ball", param=1)) #param=1はボールをキャッチする

    # ===============================
    # tanav2_positionのコールバック。(アームを中立状態にする命令を送るためのもの)
    # ===============================
    # def tanav2_position_cb(self, msg: Bool):
    #     self.GC_pub.publish(GeneralCommand(target="ball", param=4)) #param=4はアームを中立状態にする
    #     self.get_logger().info('中立位置にするように命令を送りました。')

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




def main():
    rclpy.init()
    node = BallCatch()
    rclpy.spin(node)
    rclpy.shutdown()