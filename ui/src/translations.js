const translations = {
  en: {
    welcome: 'Welcome to useyourai! Ask for a set of exercises on any language topic — for example, "Give me 10 German accusative case exercises".',
    afterEach: 'After each',
    atTheEnd: 'At the end',
    placeholderAnswer: 'Type your answer...',
    placeholderPrompt: "Ask for exercises, e.g. 'Give me 5 German adjective exercises'",
    correct: 'Correct!',
    incorrect: 'Incorrect.',
    sessionComplete: (correct, total) => `Session complete! Score: ${correct}/${total}.`,
    startNew: 'Start a new session to continue practising.',
    retryPrompt: (count) => `You got ${count} wrong. Want to practice them again?`,
    retryYes: 'Retry mistakes',
    retryNo: 'Start new session',
    error: 'Sorry, something went wrong. Please try again.',
  },
  uk: {
    welcome: 'Ласкаво просимо до useyourai! Попросіть набір вправ на будь-яку мовну тему — наприклад, «Дайте мені 10 вправ на знахідний відмінок у німецькій».',
    afterEach: 'Після кожної',
    atTheEnd: 'Наприкінці',
    placeholderAnswer: 'Введіть відповідь...',
    placeholderPrompt: "Попросіть вправи, напр. «Дайте мені 5 вправ з прикметниками»",
    correct: 'Правильно!',
    incorrect: 'Неправильно.',
    sessionComplete: (correct, total) => `Сесію завершено! Рахунок: ${correct}/${total}.`,
    startNew: 'Розпочніть нову сесію, щоб продовжити практику.',
    retryPrompt: (count) => `Ви помилилися ${count} рази. Хочете повторити?`,
    retryYes: 'Повторити помилки',
    retryNo: 'Нова сесія',
    error: 'Вибачте, щось пішло не так. Спробуйте ще раз.',
  },
};

export default translations;
