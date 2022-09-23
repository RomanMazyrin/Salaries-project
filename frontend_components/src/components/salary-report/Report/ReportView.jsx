import classNames from "classnames";
import { useStore } from "effector-react";
import { EditableMetricaView } from "../Metrica/EditableMetricaView";
import { createMetrica } from "../Metrica/factory";
import { NotEditableMetricaView } from "../Metrica/NotEditableMetricaView";
import { dateFormat } from "./ReportModel";


const REPORT_STATUSES_LABELS = {
    NOT_CONFIRMED: "Не подтвержден",
    CONFIRMED_FOR_PAYMENT: "Подтвержден для оплаты",
    PAID: "Оплачен",
    DECLINED: "Отклонен"
}

const REPORT_STATUSES_CSS_CLASSES = {
    NOT_CONFIRMED: "secondary",
    CONFIRMED_FOR_PAYMENT: "warning",
    PAID: "success",
    DECLINED: "danger",
}

const ReportView = ({ model }) => {

    const employee = useStore(model.$employee);
    const date_from = dateFormat(useStore(model.$date_from));
    const date_to = dateFormat(useStore(model.$date_to));
    const status = useStore(model.$status);
    const css_class = REPORT_STATUSES_CSS_CLASSES[status];
    const is_editable = useStore(model.$is_editable);

    const metrics = useStore(model.$metrics);

    const metricsList = metrics.map((metricaModel, i) => (
            is_editable && (metricaModel.label !== 'total_money') ? 
            <EditableMetricaView metricaModel={metricaModel} reportModel={model} i={i} key={i} /> :
            <NotEditableMetricaView metricaModel={metricaModel} key={i} />
        )
    );

    return (
        <div className="card">
            <div className="card-header">
                <h4 className="card-title align-items-center">
                    <span className="align-middle">{ employee.name }, { date_from } - { date_to }</span>
                    <span className={classNames("badge", `bg-${css_class}`, 'align-middle', 'ms-3')}>{ REPORT_STATUSES_LABELS[status] }</span>
                </h4>
            </div>
            <div className="card-content">
                <div className="table-responsive">
                    <table className="table mb-0">
                        <thead>
                            <tr>
                                {is_editable ? <th className="text-center align-middle">Учитывать в сумме</th> : null }
                                <th className="text-center align-middle">Metrica</th>
                                <th className="text-center align-middle">Value</th>
                                {is_editable ? <th className="text-center align-middle"></th> : null }
                            </tr>
                        </thead>
                        <tbody>
                            {metricsList}

                            {is_editable ? 
                            <>
                                <tr>
                                    <td></td>
                                    <td className="text-center align-middle"></td>
                                    <td className="text-center align-middle"></td>
                                    <td className="text-center align-middle">
                                        <button className='btn btn-primary' onClick={() => model.addMetrica(createMetrica())}>+ Add</button>
                                    </td>
                                </tr>
                                <tr>
                                    <td></td>
                                    <td className="text-center align-middle"></td>
                                    <td className="text-center align-middle"></td>
                                    <td className="text-center align-middle">
                                        <button className='btn btn-success' onClick={(e) => model.saveReport()}>Save</button>
                                    </td>
                                </tr>
                            </>
                            : null }
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export {ReportView}