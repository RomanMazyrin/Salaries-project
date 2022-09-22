export const NotEditableMetricaView = ({metricaModel}) => {
    return (
        <tr className={`table-${metricaModel.class_name}`}>
            <td></td>
            <td className="text-center align-middle">
                {metricaModel.name}
            </td>

            <td className="text-center align-middle">
                {metricaModel.value}
            </td>
            <td></td>
        </tr>
    );
}