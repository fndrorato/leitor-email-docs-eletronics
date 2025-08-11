// utils/num2word.js
const writtenNumber = require('written-number');
writtenNumber.defaults.lang = 'es';

module.exports = function num2word(valor) {
  return writtenNumber(valor);
};
