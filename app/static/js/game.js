var timerLength = 100;
var timerInterval = 150;
var timerHandle = 0;
var currentAnswer = null;
var num1 = 0;
var num2 = 0;

var ironman = false;

var totalQuestions = 101;
var numAnswered = 0;
var numRemaining = 101;
var numCorrect = 0;
var accuracy = 0.0;

var gameOption = null;

var startTime;
var endTime;

function sleep(ms) {
    return new Promise(
        resolve => { setTimeout(resolve, ms); }
    );
}

function timerRanOut() {
    submitAnswer();
}

function newQuestion() {
    timerLength = 101;
    runTimer();
    num1 = parseInt(1 + Math.random() * 10);
    num2 = parseInt(1 + Math.random() * 10);

    document.getElementById('questionTxt').innerHTML = `${num1} + ${num2} = `;
    clearAnswer();
    document.getElementById('feedbackTxt').innerHTML = '';

    numRemaining--;
    document.getElementById('remainingTxt').innerHTML = `${numRemaining}`;

    enableInputs();
    enableTimer();
}

function addNumber(num) {
    if (currentAnswer === null) {
        currentAnswer = num;
    } else {
        currentAnswer = 10 * currentAnswer + num;
    }

    document.getElementById('answerTxt').innerHTML = `${currentAnswer}`;
}

function generateHandler(index) {
    function handler() {
        addNumber(index);
    }

    return handler;
}

function clearAnswer() {
    currentAnswer = null;
    document.getElementById('answerTxt').innerHTML = `__`;
}

async function submitAnswer() {
    disableInputs();
    disableTimer();

    let gameOver = false;
    if (currentAnswer === num1 + num2) {
        document.getElementById('feedbackTxt').innerHTML = '&#x2714;';
        numCorrect++;
    } else {
        if (ironman) {
            gameOver = true;
        }
        document.getElementById('feedbackTxt').innerHTML = '&#x2716;';
    }

    if (currentAnswer !== null) {
        numAnswered++;
        document.getElementById('answeredTxt').innerHTML = `${numAnswered}`;
    }

    accuracy = Math.round(numCorrect / numAnswered * 100);
    document.getElementById('accuracyTxt').innerHTML = `${accuracy}%`;

    await sleep(500);

    if (numRemaining > 0 && !gameOver) {
        newQuestion();
    } else {
        finishGame();
    }
}

function runTimer() {
    if (timerLength == 0) {
        timerRanOut();
    } else {
        timerLength--;

        let timerBar = document.getElementById('timerBar');
        timerBar.style.width = `${timerLength}%`;
        timerBar.setAttribute('aria-valuenow', `${timerLength}`);
    }
}

function enableInputs() {
    for (let i = 0; i < 10; i++) {
        let btnI = document.getElementById('btn' + i);
        btnI.onclick = generateHandler(i);
    }
    document.getElementById('btnClear').onclick = clearAnswer;
    document.getElementById('btnSubmit').onclick = submitAnswer;
}

function disableInputs() {
    for (let i = 0; i < 10; i++) {
        let btnI = document.getElementById('btn' + i);
        btnI.onclick = null;
    }
    document.getElementById('btnClear').onclick = null;
    document.getElementById('btnSubmit').onclick = null;
}

function enableTimer() {
    timerHandle = setInterval(runTimer, timerInterval);
}

function disableTimer() {
    clearInterval(timerHandle);
}

async function startGame(option) {
    gameOption = option;

    let response = await fetch(`/config/${option}`, {
        'method':'POST'
    });
    let game_options = await response.json();

    if (game_options['status'] == 'ok') {
        numRemaining = totalQuestions = game_options['num_questions'];
        timerInterval = game_options['timer_interval'];
        ironman = game_options['ironman'];
    }

    startTime = new Date();
    
    newQuestion();
}

function createFormValue(name, value) {
    let val = document.createElement('input');
    val.type = 'hidden';
    val.name = name;
    val.value = value;
    return val;
}

function createFormAndSubmit(path, keyVals) {
    let f = document.createElement('form');
    f.method = 'post';
    f.action = path;

    for (key in keyVals) {
        let val = createFormValue(key, keyVals[key]);
        f.appendChild(val);
    }

    document.body.appendChild(f);
    f.submit();
}

function finishGame() {
    let accuracy = Math.round(numCorrect/numAnswered * 10000) / 100;
    let final_score = numAnswered/totalQuestions * accuracy;
    final_score = Math.round(final_score * 100) / 100;

    endTime = new Date();
    let total_time = Math.round((endTime - startTime) / 1000); // seconds

    createFormAndSubmit(
        '/finish',
        {
            'game_mode':gameOption,
            'num_questions':totalQuestions,
            'num_answered':numAnswered,
            'num_correct':numCorrect,
            'accuracy':accuracy,
            'final_score':final_score,
            'total_time':total_time
        }
    );
}

async function countdown(option) {
    let num = 5;

    for (let i = num; i > 0; i--) {
        document.getElementById('timeTxt').innerHTML = `${i}`; 
        await sleep(1000);
    }

    createFormAndSubmit(
        '/game',
        {
            'option':option
        }
    );
}