// CodeVision - Contest Timer & Leaderboard
let contestTimerInterval = null;

function initContestTimer(durationMinutes) {
    let remainingSeconds = durationMinutes * 60;
    const timerDisplay = document.getElementById('contest-timer-display');

    if (contestTimerInterval) clearInterval(contestTimerInterval);
    contestTimerInterval = setInterval(() => {
        if (remainingSeconds <= 0) {
            clearInterval(contestTimerInterval);
            if (timerDisplay) timerDisplay.innerText = "00:00:00 - Contest Ended";
            CodeVision.toast("Contest time is up!", "warning");
            return;
        }
        remainingSeconds--;
        const hrs = Math.floor(remainingSeconds / 3600);
        const mins = Math.floor((remainingSeconds % 3600) / 60);
        const secs = remainingSeconds % 60;
        if (timerDisplay) {
            timerDisplay.innerText = `${String(hrs).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
        }
    }, 1000);
}
