MODULE FCSensorCalib
!======================================================================================================
! Author      : Farzaneh Eskandari
! Email       : farzane.eskandarii@gmail.com
! Date        : 2026-06-30
!
! Force sensor calibration (ABB Force Control, IRC5). Two entry points:
!
!   CalibForceSensor  - FULL calibration. Runs FCLoadID to measure
!                       mass/CoG, then FCCalib. Use when the load CHANGES (new
!                       gripper, etc.) or for the first calibration of a load.
!                       Clear the cell; mind the camera cable (limited ax5/ax6).
!
!   QuickCalib        - FAST re-calibration, NO motion. Reuses the persisted
!                       identified_load and just re-applies FCCalib. Use at session
!                       startup after a restart, when the physical load is unchanged.
!
! Calibration state does NOT survive a controller restart (only the PERS load
! values do). QuickCalib makes that motion-free.
! Both routines set fc_calibrated := TRUE to release the streaming task (T_FORCE).
!
! Run with NO contact forces present, load physically unchanged from last FCLoadID.
!======================================================================================================

    ! ---- persistent results (survive restart; keep the real measured values) ----
    PERS loaddata identified_load := [18.9655, [-5.36228, 1.61029, 95.1608], [1,0,0,0], 0, 0, 0];
    PERS num idErr := 0.00489086;

    ! ---- cross-task flag: streaming task waits until this is TRUE ----
    PERS bool fc_calibrated := FALSE;

    ! ============================================================
    ! FULL calibration - identifies the load
    ! ============================================================
    PROC CalibForceSensor()
        VAR fcforcevector ft;

        identified_load := FCLoadID(\MaxMoveAx5:=60 \MaxMoveAx6:=60 \LoadidErr:=idErr);

        TPWrite "mass    = " \Num:=identified_load.mass;
        TPWrite "cog_x   = " \Num:=identified_load.cog.x;
        TPWrite "cog_y   = " \Num:=identified_load.cog.y;
        TPWrite "cog_z   = " \Num:=identified_load.cog.z;
        TPWrite "loadErr = " \Num:=idErr;

        FCCalib identified_load;
        fc_calibrated := TRUE;

        ft := FCGetForce(\ContactForce);
        TPWrite "Fz rest = " \Num:=ft.zforce;
    ENDPROC

    ! ============================================================
    ! QUICK calibration - no motion, reuses stored identified_load
    ! Use at session startup after a restart (load unchanged)
    ! ============================================================
    PROC QuickCalib()
        FCCalib identified_load;
        fc_calibrated := TRUE;
        TPWrite "Recalibrated from stored load, mass = " \Num:=identified_load.mass;
    ENDPROC

ENDMODULE