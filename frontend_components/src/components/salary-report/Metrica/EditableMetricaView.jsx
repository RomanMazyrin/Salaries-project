import _ from "lodash";

export const EditableMetricaView = ({metricaModel, reportModel, i}) => {

    const count_in_sum = _.get(metricaModel, "meta_params.COUNT_IN_TOTAL_SUM", false);

    return (
        <tr className={`table-${metricaModel.class_name}`}>

            <td className="text-center align-middle">
                <input 
                    type='checkbox'
                    onChange={(e) => reportModel.updateMetricaMetaParam({i, key: 'COUNT_IN_TOTAL_SUM', value: e.target.checked})}
                    checked={count_in_sum}
                    value={count_in_sum}  /> 
            </td>

            <td className="text-center align-middle">
                <input 
                    type='text'
                    value={metricaModel.name}
                    onChange={(e) => reportModel.updateMetrica({i, key: 'name', value: e.currentTarget.value})}  />
            </td>

            <td className="text-center align-middle">
                <input
                    type='text'
                    value={metricaModel.value}
                    onChange={(e) => reportModel.updateMetrica({i, key: 'value', value: e.currentTarget.value})} />
            </td>

            <td>
                <button className='btn btn-danger' onClick={() => reportModel.removeMetrica(i)}>Remove</button>
            </td>

        </tr>
    );
}