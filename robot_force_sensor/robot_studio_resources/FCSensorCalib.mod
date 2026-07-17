MODULE FCSensorCalib
!======================================================================================================
! Author      : Farzaneh Eskandari
! Email       : farzane.eskandarii@gmail.com
! Date        : 2026-06-30
!
! Force sensor calibration (ABB Force Control, IRC5). Two entry points:
!
!   CalibForceSensor  - FULL calibration. Runs FCLoadID (axes 5+6 move) to measure
!                       mass/CoG, then FCCalib. Use when the load CHANGES (new
!                       gripper, etc.) or for the first calibration of a load.
!                       Clear the cell; mind the camera cable (limited ax5/ax6).
!
!   QuickCalib        - FAST re-calibration, NO motion. Reuses the persisted
!                       identified_load and just re-applies FCCalib. Use at session
!                       startup after a restart, when the physical load is unchanged.
!
! Calibration state does NOT survive a controller restart (only the PERS load
! values do), so FCCalib must run every session. QuickCalib makes that motion-free.
! Both routines set fc_calibrated := TRUE to release the streaming task (T_FORCE).
!
! Current load: sensor + SWK-160/SWA-160 + Joulin gripper + Azure Kinect + PhoXi
! MotionCam-3D (both cameras on the eye-in-hand bracket).
!   mass    = 20.2344 kg   (was 18.9655 before the PhoXi was added, +1.27 kg)
!   cog     = [-18.94, -2.83, 92.66] mm  (lateral offset grew with the 2nd camera)
!   loadErr = 0.0059  (<< 0.1, geometry sound)
!
!
! Run with NO contact forces present, load physically unchanged from last FCLoadID.
!======================================================================================================

    ! ---- persistent results (survive restart; keep the real measured values) ----
    PERS loaddata identified_load := [20.2344, [-18.9364, -2.83072, 92.658], [1,0,0,0], 0, 0, 0];
    PERS num idErr := 0.00586962; 

    ! ---- cross-task flag: streaming task waits until this is TRUE ----
    PERS bool fc_calibrated := FALSE;

    ! ============================================================
    ! FULL calibration - moves axes 5 and 6, identifies the load
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