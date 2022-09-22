import axios from "axios";
import { render } from "react-dom";
import { ReportView, ReportModel } from "./../src/index";
import "./../../src/salaries/static/salaries/css/bootstrap.min.css";

(async () => {

    const res = await axios.get(`http://localhost/api/salary-report/aiXSo3ax`, {
        "params": {}
    });

    const report = new ReportModel(res.data, true);
    
    render(<ReportView model={report}/>, document.getElementById('content'));
    
})();