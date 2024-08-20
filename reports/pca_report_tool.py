from .utils import PCAdataTool


def process_report_data(form_data):
    # Assuming `form_data` is a dictionary with keys similar to the config file
    surveyor = form_data.get('surveyor')
    company = form_data.get('company')
    inspection_time = form_data.get('report_timestamp')
    address = form_data.get('property_address')

    occupied = form_data.get('occupied')
    monitor_time = form_data.get('occupied_during_all_monitoring')
    occupant_number = form_data.get('number_of_occupants')

    # Handling images
    image_logo = form_data.get('company_logo')
    external_picture = form_data.get('external_picture')
    room_picture = form_data.get('room_picture')

    problemRooms = [form_data.get('room_name')]
    problemAreas = [form_data.get('room_monitor_area')]
    varMoulds = [form_data.get('room_mould_visible')]

    # Collecting logger data files (assuming these are already processed and saved as CSV or similar)
    inputFiles = [
        form_data.get('external_logger_data'),
        form_data.get('ambient_logger_data'),
        form_data.get('surface_logger_data')
    ]

    comments = form_data.get('notes')

    # Assuming `PCAdataTool.RPTGen` can accept these directly:
    PCAdataTool.RPTGen(
        inputFiles=inputFiles,
        surveyor=surveyor,
        inspection_time=inspection_time,
        company=company,
        address=address,
        occupied=occupied,
        monitor_time=monitor_time,
        occupant_number=occupant_number,
        problemRooms=problemRooms,
        problemAreas=problemAreas,
        varMoulds=varMoulds,
        image_property=external_picture,
        image_indoor1=room_picture,  # Assuming room_picture is a representative image
        image_indoor2=None,
        image_indoor3=None,
        image_indoor4=None,
        image_logo=image_logo,
        comments=comments,
        popup=False
    )