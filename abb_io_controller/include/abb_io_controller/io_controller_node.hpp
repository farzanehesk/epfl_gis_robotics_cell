/***********************************************************************
 * Package:     abb_io_controller
 * File:        io_controller_node.hpp
 * Description: ROS2 node exposing tool changer lock/unlock services
 *              and a vacuum gripper GripperCommand action, both
 *              implemented via ABB RWS digital I/O signals.
 * Robot:       ABB IRB6700 175/3.05 on IRBT6004 7m rail
 * Author:      Farzaneh Eskandari
 * Email:       farzane.eskandarii@gmail.com
 * Date:        2026-06-10
 ***********************************************************************/

#ifndef ABB_IO_CONTROLLER_IO_CONTROLLER_NODE_HPP
#define ABB_IO_CONTROLLER_IO_CONTROLLER_NODE_HPP

#include <memory>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <control_msgs/action/gripper_command.hpp>

#include <abb_egm_rws_managers/rws_manager.h>

namespace abb_io_controller
{

// ============================================================
// PLACEHOLDER SIGNAL NAMES — confirm against IRC5 I/O config
// and update before use.
// ============================================================
namespace signals
{
  constexpr const char* TOOL_CHANGER_RELEASE = "Local_IO_0_DO9";  // 1 = release, 0 = locked
  constexpr const char* VACUUM_ON            = "Local_IO_0_DO1";  // 1 = air on (grip), 0 = off (release)
  //constexpr const char* TOOL_CHANGER_LOCKED_FB = "DI_ToolChangerLocked"; // optional feedback
}


class IOControllerNode : public rclcpp::Node
{
public:
  using GripperCommand = control_msgs::action::GripperCommand;
  using GoalHandleGripper = rclcpp_action::ServerGoalHandle<GripperCommand>;

  IOControllerNode(std::shared_ptr<abb::robot::RWSManager> rws_manager);

private:
  // --- Tool changer services ---
  void handleLock(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response);

  void handleUnlock(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response);


  // --- Vacuum gripper action ---
  rclcpp_action::GoalResponse handleGripperGoal(
    const rclcpp_action::GoalUUID& uuid,
    std::shared_ptr<const GripperCommand::Goal> goal);

  rclcpp_action::CancelResponse handleGripperCancel(
    const std::shared_ptr<GoalHandleGripper> goal_handle);

  void handleGripperAccepted(
    const std::shared_ptr<GoalHandleGripper> goal_handle);

  void executeGripperCommand(
    const std::shared_ptr<GoalHandleGripper> goal_handle);

  // --- Helper ---
  bool setSignal(const std::string& signal_name, const std::string& value);

  std::shared_ptr<abb::robot::RWSManager> rws_manager_;

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr lock_srv_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr unlock_srv_;
  rclcpp_action::Server<GripperCommand>::SharedPtr gripper_action_server_;
};

}  // namespace abb_io_controller

#endif  // ABB_IO_CONTROLLER_IO_CONTROLLER_NODE_HPP