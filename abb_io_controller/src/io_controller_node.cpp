/***********************************************************************
 * Package:     abb_io_controller
 * File:        io_controller_node.cpp
 * Description: Implementation of IOControllerNode — see header.
 * Robot:       ABB IRB6700 175/3.05 on IRBT6004 7m rail
 * Author:      Farzaneh Eskandari
 * Email:       farzane.eskandarii@gmail.com
 * Date:        2026-06-10
 ***********************************************************************/

#include "abb_io_controller/io_controller_node.hpp"

namespace abb_io_controller
{

IOControllerNode::IOControllerNode(std::shared_ptr<abb::robot::RWSManager> rws_manager)
: Node("abb_io_controller_node"), rws_manager_(rws_manager)
{
  lock_srv_ = create_service<std_srvs::srv::Trigger>(
    "/tool_changer/lock",
    std::bind(&IOControllerNode::handleLock, this,
              std::placeholders::_1, std::placeholders::_2));

  unlock_srv_ = create_service<std_srvs::srv::Trigger>(
    "/tool_changer/unlock",
    std::bind(&IOControllerNode::handleUnlock, this,
              std::placeholders::_1, std::placeholders::_2));

  gripper_action_server_ = rclcpp_action::create_server<GripperCommand>(
    this,
    "/gripper/gripper_cmd",
    std::bind(&IOControllerNode::handleGripperGoal, this,
              std::placeholders::_1, std::placeholders::_2),
    std::bind(&IOControllerNode::handleGripperCancel, this, std::placeholders::_1),
    std::bind(&IOControllerNode::handleGripperAccepted, this, std::placeholders::_1));

  RCLCPP_INFO(get_logger(), "abb_io_controller_node started");
  RCLCPP_INFO(get_logger(), "  /tool_changer/lock, /tool_changer/unlock services ready");
  RCLCPP_INFO(get_logger(), "  /gripper/gripper_cmd action server ready");
}

// --- Helper ---

bool IOControllerNode::setSignal(const std::string& signal_name, const std::string& value)
{
  bool success = false;
  rws_manager_->runPriorityService(
    [&](abb::rws::RWSStateMachineInterface& interface)
    {
      success = interface.setIOSignal(signal_name, value);
    });

  if (!success)
  {
    RCLCPP_ERROR(get_logger(), "Failed to set signal '%s' to '%s'",
                 signal_name.c_str(), value.c_str());
  }
  return success;
}

// --- Tool changer ---

void IOControllerNode::handleLock(
  const std::shared_ptr<std_srvs::srv::Trigger::Request> /*request*/,
  std::shared_ptr<std_srvs::srv::Trigger::Response> response)
{
  RCLCPP_INFO(get_logger(), "Tool changer LOCK requested");
  bool ok = setSignal(signals::TOOL_CHANGER_RELEASE, "0");  // 0 = locked
  response->success = ok;
  response->message = ok ? "Tool changer locked" : "Failed to lock tool changer";
}

void IOControllerNode::handleUnlock(
  const std::shared_ptr<std_srvs::srv::Trigger::Request> /*request*/,
  std::shared_ptr<std_srvs::srv::Trigger::Response> response)
{
  RCLCPP_INFO(get_logger(), "Tool changer UNLOCK requested");
  bool ok = setSignal(signals::TOOL_CHANGER_RELEASE, "1");  // 1 = release
  response->success = ok;
  response->message = ok ? "Tool changer unlocked" : "Failed to unlock tool changer";
}


// --- Vacuum gripper ---

rclcpp_action::GoalResponse IOControllerNode::handleGripperGoal(
  const rclcpp_action::GoalUUID& /*uuid*/,
  std::shared_ptr<const GripperCommand::Goal> goal)
{
  RCLCPP_INFO(get_logger(), "Gripper goal received: position=%.2f", goal->command.position);
  return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse IOControllerNode::handleGripperCancel(
  const std::shared_ptr<GoalHandleGripper> /*goal_handle*/)
{
  return rclcpp_action::CancelResponse::ACCEPT;
}

void IOControllerNode::handleGripperAccepted(
  const std::shared_ptr<GoalHandleGripper> goal_handle)
{
  // Execute in a new thread to avoid blocking the executor
  std::thread{std::bind(&IOControllerNode::executeGripperCommand, this, goal_handle)}.detach();
}

void IOControllerNode::executeGripperCommand(
  const std::shared_ptr<GoalHandleGripper> goal_handle)
{
  const auto goal = goal_handle->get_goal();
  auto result = std::make_shared<GripperCommand::Result>();

  // position > 0.5 -> vacuum ON (grip), else OFF (release)
  bool vacuum_on = goal->command.position > 0.5;
  std::string value = vacuum_on ? "1" : "0";

  RCLCPP_INFO(get_logger(), "Setting vacuum signal '%s' to '%s'",
              signals::VACUUM_ON, value.c_str());

  bool ok = setSignal(signals::VACUUM_ON, value);

  result->position = goal->command.position;
  result->reached_goal = ok;
  result->stalled = false;

  if (ok)
  {
    goal_handle->succeed(result);
  }
  else
  {
    goal_handle->abort(result);
  }
}

}  // namespace abb_io_controller