function throwDices(dices) {
    let result = 0;
    message = [];
    console.log('Вы кидаете кубики (' + dices + ')...')
    for (let dice = 1; dice <= dices; dice++) {
        let points = Math.floor(Math.random() * 6) + 1;
        message.push(points);
        result += points;
    }
    console.log('Вы выбросили [' + message + '] = ' + result);
    return result
}

throwDices(2);
