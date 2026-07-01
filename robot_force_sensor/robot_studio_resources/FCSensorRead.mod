MODULE FCSensorRead
!======================================================================================================
! Author      : Farzaneh Eskandari
! Email       : farzane.eskandarii@gmail.com -farzaneh.eskandari@epfl.ch
! Date        : 2026-06-30
!
! Force sensor live-read routine (ABB Force Control, IRC5).
! Purpose: continuously read gravity-compensated contact force/torque and expose
!          it as a PERS so it can be watched live in the RobotStudio Watch window.
!          Used for the post-calibration push test (verify rest ~0, responds to push).
!
!   - No robot motion. Requires the sensor to be calibrated (FCCalib already run),
!     otherwise FCGetForce(\ContactForce) returns error 50323.
!   - ft_live updates ~10 Hz; add it to the RobotStudio Watch window to see
!     Fx/Fy/Fz/Tx/Ty/Tz change in real time while pushing the gripper.
!   - Stop with the program stop button when done.
!
! Expected behavior (calibrated, gripper free, no contact):
!   all six components near zero -> push down -> Fz responds -> release -> back to ~0
!
! ft_live fields: xforce yforce zforce (N), xtorque ytorque ztorque (Nm)
!======================================================================================================

    ! ---- live force/torque, readable in the RobotStudio Watch window ----
    PERS fcforcevector ft_live := [0, 0, 0, 0, 0, 0];

    PROC ReadForceLoop()
        WHILE TRUE DO
            ft_live := FCGetForce(\ContactForce);
            WaitTime 0.1;
        ENDWHILE
    ENDPROC

ENDMODULE