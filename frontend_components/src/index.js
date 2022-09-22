import { ReportModel } from "./components/salary-report/Report/ReportModel";
import { ReportView } from "./components/salary-report/Report/ReportView";
import axios from "axios";
import { render } from "react-dom";

const renderSalaryReportForm = async (report_slug, element_id) => {
    const res = await axios.get(`/api/salary-report/${report_slug}`);
    const report = new ReportModel(res.data, true);
    render(<ReportView model={report}/>, document.getElementById(element_id));
};

export {
    renderSalaryReportForm
}