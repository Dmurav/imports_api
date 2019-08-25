from django.db import transaction

from imports.api.models import DataSet, Citizen, CitizenRelative


@transaction.atomic
def create_dataset(citizens):
    data_set = DataSet.objects.create()

    citizen_models = []
    citizen_pairs = []
    for cit_data in citizens:

        cid = cit_data['citizen_id']
        for rid in cit_data['relatives']:
            citizen_pairs.append((cid, rid))

        cit_data.pop('relatives')
        cit = Citizen(**cit_data)
        cit.data_set = data_set
        citizen_models.append(cit)

    Citizen.objects.bulk_create(citizen_models)

    # insert into many-to-many relationship
    ids = {}
    citizen_ids = (Citizen.objects
                   .filter(data_set=data_set).values_list('id', 'citizen_id'))
    for cid, citizen_id in citizen_ids:
        ids[citizen_id] = cid

    citizen_relatives = []  # pair to insert into CitizenRelative table
    for citizen_id, relative_id in citizen_pairs:
        cid, rid = ids[citizen_id], ids[relative_id]
        citizen_relatives.append(CitizenRelative(citizen_id=cid, relative_id=rid))
    CitizenRelative.objects.bulk_create(citizen_relatives)

    return data_set.id
