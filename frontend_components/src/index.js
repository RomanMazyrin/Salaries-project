import { ReportModel } from "./components/salary-report/Report/ReportModel";
import { ReportView } from "./components/salary-report/Report/ReportView";
import axios from "axios";
import { createRoot } from "react-dom/client";

const renderSalaryReportForm = async (report_slug, element_id, is_editable=false, host = "/") => {
    const API_ENTITY_URL = `${host}api/salary-report/${report_slug}`;
    const res = await axios.get(API_ENTITY_URL);
    const report = new ReportModel(res.data, is_editable, API_ENTITY_URL);

    createRoot(document.getElementById(element_id))
        .render(<ReportView model={report}/>);
};

export {
    renderSalaryReportForm
}