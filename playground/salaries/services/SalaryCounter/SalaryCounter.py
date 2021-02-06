class SalaryCounter:

    def __init__(self, onpbx_client=None):
        self.__onpbx_client = onpbx_client

    def get_detailed_report(self, employee, timestamp_from, timestamp_to):
        res_outbound = self.__onpbx_client.call_history.get(
            accountcode='outbound',
            caller_id_number=str(employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            duration_from=21
        )

        res_inbound = self.__onpbx_client.call_history.get(
            accountcode='inbound',
            destination_number=str(employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            user_talk_time_from=21
        )

        sal = int((len(res_outbound) + len(res_inbound)) * employee.one_call_cost)

        return {
            "money": sal,
            'calls_outbound_count': len(res_outbound),
            'calls_inbound_count': len(res_inbound),
            'calls_total_count': len(res_inbound) + len(res_outbound),
        }
