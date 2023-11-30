import copy

import pytest
from fastapi import HTTPException

from app.crud.crud_company import CRUDCompany
from app.schemas.ad import AdCreate, AdStatusCreate, SkillLevel, ResumeStatus, AdSkills
from app.db.models import DbAds, DbJobsMatches
from app.crud.crud_ad import create_ad_crud, get_resumes_crud, get_job_ads_crud, update_resumes_crud, \
    update_job_ads_crud, delete_ad_crud, get_skills_crud, add_skill_to_ad_crud, remove_skill_from_ad_crud, get_ad, \
    get_skill, create_new_skill


from tests.api.api_v1.endpoints.ad_test import create_company, create_ad, create_info, create_professional, \
    create_skill, ad_data_list


@pytest.mark.asyncio
async def test_create_ad_crud_raise_404_bad_request(db, test_db):
    user, company = await create_company(db)

    schema = AdCreate(
        description='dummyDescription',
        location='dummyLocation',
        status=AdStatusCreate.ACTIVE,
        min_salary=1500,
        max_salary=3000
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_ad_crud(db, user, schema)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Complete your info before creating an ad'


@pytest.mark.asyncio
async def test_get_resumes_filter_ads_returns_correct_data(db, test_db):
    ad_data_list_all_resumes = copy.deepcopy(ad_data_list)
    for ad in ad_data_list_all_resumes:
        ad['is_resume'] = True

    ads = [DbAds(**ad) for ad in ad_data_list_all_resumes]
    db.add_all(ads)
    db.commit()

    result = await get_resumes_crud(db, description='dummy desc')
    assert len(result) == 3  # 3 as one is_deleted

    result = await get_resumes_crud(db, location='Sofia')
    assert len(result) == 1  # Only 1 is in Sofia
    assert result[0].description == "dummy desc1"

    result = await get_resumes_crud(db, ad_status=ResumeStatus.PRIVATE)
    assert len(result) == 1  # Only 1 is private
    assert result[0].description == 'dummy desc2'

    result = await get_resumes_crud(db, min_salary=1400, max_salary=2600)
    assert len(result) == 2  # Two respect the price range
    assert result[0].description == 'dummy desc2'
    assert result[1].description == 'dummy desc3'


@pytest.mark.asyncio
async def test_get_resumes_crud_raises_404_not_found(db, test_db):
    ad_data_list_all_job_ads = copy.deepcopy(ad_data_list)
    for ad in ad_data_list_all_job_ads:
        ad['is_resume'] = False

    ads = [DbAds(**ad) for ad in ad_data_list_all_job_ads]
    db.add_all(ads)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_resumes_crud(db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There are no results for your search"


@pytest.mark.asyncio
async def test_get_job_ads_crud_raises_404_not_found(db, test_db):
    ad_data_list_all_resumes = copy.deepcopy(ad_data_list)
    for ad in ad_data_list_all_resumes:
        ad['is_resume'] = True

    ads = [DbAds(**ad) for ad in ad_data_list_all_resumes]
    db.add_all(ads)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_job_ads_crud(db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There are no results for your search"


@pytest.mark.asyncio
async def test_update_resumes_crud_raises_400_bad_request(db, test_db):
    user, company = await create_company(db)
    info = await create_info(db)
    ad = await create_ad(db, info)

    with pytest.raises(HTTPException) as exc_info:
        await update_resumes_crud(db, user, ad_id=ad.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Cannot update job ads'


@pytest.mark.asyncio
async def test_update_job_ads_crud_raises_400_bad_request(db, test_db):
    user, professional = await create_professional(db)
    info = await create_info(db)
    ad = await create_ad(db, info)

    ad.is_resume = True
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await update_job_ads_crud(db, user, ad_id=ad.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Cannot update resumes'


@pytest.mark.asyncio
async def test_delete_ad_crud_raises_403_forbidden(db, test_db):
    user, company = await create_company(db)
    info = await create_info(db)
    ad = await create_ad(db, info)

    with pytest.raises(HTTPException) as exe_info:
        await delete_ad_crud(db, ad.id, user)

    assert exe_info.value.status_code == 403
    assert exe_info.value.detail == 'Only the author can apply changes'


@pytest.mark.asyncio
async def test_delete_ad_crud_set_info_main_resume_back_to_none(db, test_db):
    user, professional = await create_professional(db)
    info = await create_info(db)
    professional.info_id = info.id

    ad = await create_ad(db, info)
    info.main_ad = ad.id
    db.commit()

    await delete_ad_crud(db, ad.id, user)

    assert info.main_ad is None


@pytest.mark.asyncio
async def test_get_skills_crud_raises_404_not_found(db, test_db):
    with pytest.raises(HTTPException) as exc_info:
        await get_skills_crud(db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'There are no available skills to display, add a skill first'


@pytest.mark.asyncio
async def test_add_skill_to_ad_crud_raises_400_bad_request(db, test_db):
    user, professional = await create_professional(db)
    info = await create_info(db)
    professional.info_id = info.id
    db.commit()

    ad = await create_ad(db, info)
    skill = await create_skill(db)

    await add_skill_to_ad_crud(db, ad.id, skill.name, level=SkillLevel.BEGINNER)

    with pytest.raises(HTTPException) as exc_info:
        await add_skill_to_ad_crud(db, ad.id, skill.name, level=SkillLevel.ADVANCED)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"'{skill.name}' already added to this ad"


@pytest.mark.asyncio
async def test_remove_skill_from_ad_crud_raises_404_not_found(db, test_db):
    user, professional = await create_professional(db)
    info = await create_info(db)
    professional.info_id = info.id
    db.commit()

    ad = await create_ad(db, info)
    skill = await create_skill(db)

    with pytest.raises(HTTPException) as exc_info:
        await remove_skill_from_ad_crud(db, ad.id, skill.name)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"'{skill.name}' does not exist in this ad"


@pytest.mark.asyncio
async def test_get_ad_raises_404_not_found(db, test_db):
    info = await create_info(db)
    ad = await create_ad(db, info)
    ad.is_deleted = True
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_ad(db, ad.id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Ad not found'


@pytest.mark.asyncio
async def test_get_skill_raises_404_not_found(db, test_db):
    skill = await create_skill(db)
    skill.is_deleted = True
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_skill(db, skill.name)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Skill not found'


@pytest.mark.asyncio
async def test_new_skill_already_exists_raises_400_bad_request(db, test_db):
    await create_skill(db)

    new_skill = AdSkills(name='dummySkill')

    with pytest.raises(HTTPException) as exc_info:
        await create_new_skill(db, new_skill)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Skill with name '{new_skill.name}' already exists"


@pytest.mark.asyncio
async def test_delete_ad_deletes_job_matches(db, test_db):
    user1, professional = await create_professional(db)
    professional_info = await create_info(db)
    professional.info_id = professional_info.id
    professional_ad = await create_ad(db, professional_info)
    professional_ad.is_resume = True

    user, company = await create_company(db)
    company_info = await create_info(db)
    company.info_id = company_info.id
    company_ad = await create_ad(db, company_info)

    db.commit()

    match = DbJobsMatches(
        ad_id=company_ad.id,
        resume_id=professional_ad.id,
        company_id=company.id,
        professional_id=professional.id
    )

    db.add(match)
    db.commit()

    await delete_ad_crud(db, company_ad.id, user)
    await delete_ad_crud(db, professional_ad.id, user1)

    result = await CRUDCompany.get_matches_multi(db, company)

    assert len(result) == 0
