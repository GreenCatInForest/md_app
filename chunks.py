        <table class="min-w-full bg-white text-gray-900 shadow-md rounded-lg overflow-hidden">
            <thead class="bg-gray-100">
                <tr>
                    <th class="py-2 px-4 border-b-2 border-gray-200 text-left text-gray-700">Date of Report</th>
                    <th class="py-2 px-4 border-b-2 border-gray-200 text-left text-gray-700">Property Address</th>
                    <th class="py-2 px-4 border-b-2 border-gray-200 text-left text-gray-700">Survey time</th>
                    <!-- <th class="py-2 px-4 border-b-2 border-gray-200 text-left text-gray-700">Rooms Name</th> -->
                    <th class="py-2 px-4 border-b-2 border-gray-200 text-left text-gray-700">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for report in reports %}
                <tr class="hover:bg-gray-50">
                    <td class="py-2 px-4 border-b text-gray-900">{{ report.report_timestamp|date:"Y-m-d" }}</td>
                    <td class="py-2 px-4 border-b text-gray-900">{{ report.property_address }}</td>
                    <td class="py-2 px-4 border-b text-gray-900">{{ report.start_time}}</td>
                    <td class="py-2 px-4 border-b text-gray-900">
                        <p>Report Status: {{ report.status }}</p>
                        {% for payment in report.payments.all%}

                            <p>Payment ID: {{ payment.id }} Payment Status: {{payment.status}}</p>

                            {% if report.report_file and payment.status == 'succeeded'%}
                                {% if report.report_file and report.report_file.url %}
                                    <p>Report File: <a href="{{ report.report_file.url }}" target="_blank">{{ report.report_file.name }}</a></p>
                                    <a href="{% url 'download_report' report.id %}" class="text-blue-500 hover:underline">Download Report</a>
                                {% else %}
                                    <p>No report available.</p>
                                {% endif %}
                            {% elif report.report_file and payment.status == 'unpaid'%}
                                    <button class="text-blue-500 hover:underline">Pay Now</button>
                            {% elif report.report_file and payment.status == 'None'%}
                                    <p>Report likally had been paid before. Please email us.</p>
                            {% else%}
                            <p>Here is no information about payment status</p>
                            {% endif%}
                        {% endfor %}
                    </td>
                {% empty %}
                <tr>
                    <td colspan="4" class="text-center py-4 text-gray-900">No reports found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>