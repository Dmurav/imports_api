from django.db import transaction
from django.db.models import Q

from imports.api.models import DataSet, Citizen, CitizenRelative


@transaction.atomic
def create_dataset(citizens):
    data_set = DataSet.objects.create()

    citizen_models = []
    citizen_pairs = []
    for cit_data in citizens:

        cid = cit_data['citizen_id']
        for rid in set(cit_data['relatives']):
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


@transaction.atomic
def update_citizen(data_set_id, citizen_id, citizen_data):
    data_set = DataSet.objects.get(id=data_set_id)
    citizen = Citizen.objects.get(data_set=data_set, citizen_id=citizen_id)
    relatives = citizen_data.pop('relatives', None)
    Citizen.objects.filter(data_set_id=data_set_id, citizen_id=citizen_id).update(**citizen_data)

    if relatives is not None:
        # check all specified relatives exist in data set
        relatives = set(relatives)
        existing_relatives = (Citizen.objects
                              .filter(data_set_id=data_set_id, citizen_id__in=relatives)
                              .values_list('citizen_id', flat=True))
        non_existing = set(relatives) - set(existing_relatives)
        if non_existing:
            raise Citizen.DoesNotExist(f'No citizen with citizen_id in {non_existing}')

        # clean all relatives info involving citizen
        CitizenRelative.objects.filter(Q(citizen=citizen) | Q(relative=citizen)).delete()

        # new relatives for citizen
        new_relatives = Citizen.objects.filter(data_set_id=data_set_id, citizen_id__in=relatives)

        citizen_relatives = []
        for c in new_relatives:
            citizen_relatives.extend([
                CitizenRelative(citizen=citizen, relative=c),
                CitizenRelative(citizen=c, relative=citizen),

            ])

        CitizenRelative.objects.bulk_create(citizen_relatives)

    citizen.refresh_from_db()
    return citizen
