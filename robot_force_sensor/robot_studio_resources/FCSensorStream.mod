MODULE FCSensorStream
!======================================================================================================
! Author      : Farzaneh Eskandari
! Email       : farzane.eskandarii@gmail.com -farzaneh.eskandari@epfl.ch
! Date        : 2026-06-30
!
! Force sensor UDP streaming task (ABB Force Control, IRC5).
! Runs as a SEMISTATIC background task (T_FORCE), independent of T_ROB1, so force
! can stream while the arm moves under EGM.
!
! Loop: FCGetForce(\ContactForce) -> pack 6 values as ASCII -> UDP send.
!   Packet: "fx fy fz tx ty tz"  (N N N Nm Nm Nm), space separated.
!   Target: workstation 192.168.0.100 : 6520  (6511 reserved for EGM)
!
! STARTUP GUARD: the task auto-starts at boot, but calibration does NOT survive a
! restart. So it idles until fc_calibrated (set TRUE by FCSensorCalib) is TRUE,
! then begins reading. This prevents the 50323 -> 40223 -> task-death cascade that
! happens if FCGetForce is called uncalibrated at boot.
!
! Session startup: restart -> task idles -> run QuickCalib -> streaming begins.
! This task does NOT control motion.
!======================================================================================================

    VAR socketdev sock;
    VAR fcforcevector ft;
    VAR string packet;

    PERS string workstation_ip := "192.168.0.100";
    PERS num    workstation_port := 6520;

    ! ---- shared with FCSensorCalib: TRUE only after a successful FCCalib ----
    PERS bool fc_calibrated := FALSE;

    PROC main()
        fc_calibrated := FALSE;        ! force FALSE at every boot, ignore persisted value
        SocketCreate sock \UDP;

        WHILE TRUE DO
            IF fc_calibrated THEN
                ft := FCGetForce(\ContactForce);

                packet := ValToStr(ft.xforce)  + " "
                        + ValToStr(ft.yforce)  + " "
                        + ValToStr(ft.zforce)  + " "
                        + ValToStr(ft.xtorque) + " "
                        + ValToStr(ft.ytorque) + " "
                        + ValToStr(ft.ztorque) + "\0A";

                SocketSendTo sock, workstation_ip, workstation_port \Str:=packet;

                WaitTime 0.01;        ! ~100 Hz target (actual lower, RAPID-limited)
            ELSE
                WaitTime 0.5;         ! idle until calibration sets the flag
            ENDIF
        ENDWHILE
    ENDPROC

ENDMODULE