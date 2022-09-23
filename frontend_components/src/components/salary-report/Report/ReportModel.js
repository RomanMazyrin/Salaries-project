import axios from "axios";
import { combine, createEffect, createEvent, createStore, sample } from "effector";
import _ from "lodash";
import moment from "moment";

export const dateFormat = (d_string) => {
    return moment(d_string).format("DD.MM.YYYY");
};

const calculateResultReportSum = (metrics) => {
    const upd = [...metrics];
    const resultSum = upd.reduce((prev, curr, i, m) => {
        if (_.get(curr, 'meta_params.COUNT_IN_TOTAL_SUM', false)) {
            prev += parseInt(curr['value']);
        }
        return prev;
    }, 0);
    
    return upd.map(metrica => {
        if (metrica['label'] == 'total_money') {
            metrica['value'] = resultSum;
        }
        return metrica;
    });
};

const sortMetrics = (metrics) => {
    return _.sortBy(metrics, metrica => metrica.label === 'total_money' ? 1 : 0);
};

const calculateResultReport = (metrics) => {
    return sortMetrics(calculateResultReportSum(metrics));
};

export class ReportModel {
    constructor({ employee = {}, date_from = '', date_to = '', status = '', metrics = [], slug_id } = {}, is_editable = false, API_ENTITY_URL = '') {
        this.$employee = createStore(employee);
        this.$date_from = createStore(date_from);
        this.$date_to = createStore(date_to);
        this.$status = createStore(status);
        this.$metrics = createStore(metrics);
        this.$slug_id = createStore(slug_id);

        this.$is_editable = createStore(is_editable);

        this.$data = combine({
            employee: this.$employee,
            date_from: this.$date_from,
            date_to: this.$date_to,
            status: this.$status,
            metrics: this.$metrics,
            slug_id: this.$slug_id
        },
            obj => obj
        );

        this.addMetrica = createEvent();
        this.removeMetrica = createEvent();
        this.updateMetrica = createEvent();
        this.updateMetricaMetaParam = createEvent();
        this.saveReport = createEvent();


        this.$metrics
            .on(this.addMetrica, (metrics, newMetrica) => calculateResultReport([...metrics, newMetrica]))
            .on(this.removeMetrica, (metrics, index) => calculateResultReport(metrics.filter((_, i) => i !== index)))
            .on(this.updateMetrica, (metrics, params) => {
                const upd = [...metrics];
                upd[params['i']][params['key']] = params['value'];
                return calculateResultReport(upd);
            })
            .on(this.updateMetricaMetaParam, (metrics, params) => {
                const upd = [...metrics];
                _.set(upd[params['i']], `meta_params.${params['key']}`, params['value']);
                return calculateResultReport(upd);
            });

        this.saveReportFx = createEffect(async (data) => {
            const response = await axios.patch(API_ENTITY_URL, JSON.stringify(data), {
                "headers": {
                    "content-type": "application/json"
                }
            });
        });

        sample({
            source: this.$data,
            clock: this.saveReport,
            target: this.saveReportFx
        });
    }
}