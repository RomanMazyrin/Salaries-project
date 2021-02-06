import { renderSalaryReportForm } from "./../src/index";
import "./../../src/salaries/static/salaries/css/bootstrap.min.css";
import "./../../src/salaries/static/salaries/css/style.css";

(async() => {
    await renderSalaryReportForm('aiXSo3ax', 'report-form', true, "http://localhost/");
})();