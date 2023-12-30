const getCheckboxSum = (element) => {
    const sumAsText = element.parentElement.parentElement.querySelector('.field-total_money').textContent;
    const sumAsInt = parseInt(sumAsText.split(',').join(''), 10);
    return sumAsInt;
};

const writeToResultDiv = (sum) => {
    document.getElementById('total-sum-result').textContent = 'Общая сумма выбранных отчетов: ' + sum.toLocaleString('en-US');
};

const countTotalSumOfAllSelected = () => {
    return Array.from(document.querySelectorAll(".action-select[name='_selected_action']"))
        .reduce((sum, element) => {
            if (element.checked) {
                return sum + getCheckboxSum(element);
            }
            return sum;
        }, 0);
};

window.addEventListener("load", function() {
    document.body.addEventListener('change', function (e) {
        writeToResultDiv(countTotalSumOfAllSelected());
    }, false);
});