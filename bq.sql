CREATE OR REPLACE SCHEMA <<PROJECT_ID>>.<<DATASET_ID>>
  OPTIONS (
    description = 'This is the dataset for sales story application storing MDP views',
    labels = [('app','sales-story')],
    location = 'asia-south1',
    storage_billing_model = 'LOGICAL'
  );

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_testdrive_survey 
AS 
WITH ranked_leads AS (
  SELECT
    enquiry_number,
    q2_testdrive_experience,
    q38_additional_comments,
    ROW_NUMBER() OVER (
      PARTITION BY enquiry_number
      ORDER BY recorded_date DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.intello_testdrive_survey`
)
SELECT
  enquiry_number,
  q2_testdrive_experience as testdrive_experience,
  q38_additional_comments as testdrive_feeback
FROM ranked_leads
WHERE rn = 1;

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_testdrive_survey 
AS
WITH ranked_leads AS (
  SELECT
    enquiry_id__c,
    location_type__c,
    product_family__c,
    stage__c,
    contact_email__c,
    ROW_NUMBER() OVER (
      PARTITION BY enquiry_id__c
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_test_drive`
)
SELECT
  enquiry_id__c as opportunity_id,
  location_type__c as test_drive_location,
  product_family__c as test_drive_vehicle,
  stage__c as test_drive_stage,
  contact_email__c as test_drive_email
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_task 
AS
WITH ranked_leads AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY whatid
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_task`
)
SELECT
  whatid as opportunity_id,
  description as task_customer_remarks,
  dealer_remarks_type__c as task_dealer_remarks,
  product_family__c as task_product_interested,
  variant__c as task_variant_interested
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_opportunity 
AS
WITH ranked_leads AS (
  SELECT
    contact__c,
    id,
    enquiry_number__c,
    createddate,
    product_interest__c,
    completed_stages__c,
    lost_remarks_by_sales_consultant__c,
    customer_interested_comments__c,
    customer_interested_remarks__c,
    purchase_type__c,
    is_this_your_1st_mahindra_consideration__c,
    ROW_NUMBER() OVER (
      PARTITION BY contact__c
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_opportunity`
)
SELECT
  contact__c as contact_id,
  id as opportunity_id,
  enquiry_number__c as enquiry_number,
  createddate as opportunity_create_date,
  product_interest__c as opportunity_product_interested,
  completed_stages__c as opportunity_completed_stages,
  lost_remarks_by_sales_consultant__c as opportunity_lost_remarks,
  customer_interested_comments__c as opportunity_customer_comments,
  customer_interested_remarks__c as opportunity_customer_remarks,
  purchase_type__c as opportunity_purchase_type,
  is_this_your_1st_mahindra_consideration__c as opportunity_first_mahindra_consideration
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_lead 
AS
WITH ranked_leads AS (
  SELECT
    convertedcontactid,
    createddate,
    product_interest__c,
    ROW_NUMBER() OVER (
      PARTITION BY convertedcontactid
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_lead`
)
SELECT
  convertedcontactid as contact_id,
  createddate as lead_create_date,
  product_interest__c as lead_product_interested
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_contact 
AS
WITH ranked_leads AS (
  SELECT
    id,
    mobilephone,
    salutation,
    firstname,
    lastname,
    gender__c,
    mailingcity,
    mailingstate,
    occupation_name__c,
    ROW_NUMBER() OVER (
      PARTITION BY id
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_contact`
)
SELECT
  id as contact_id,
  mobilephone as mobilephone,
  salutation as salutation,
  firstname as first_name,
  lastname as last_name,
  gender__c as gender,
  mailingcity as city,
  mailingstate as state,
  occupation_name__c as occupation,
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_competitors 
AS
WITH ranked_leads AS (
  SELECT
    enquiry__c,
    make__c,
    model__c,
    ROW_NUMBER() OVER (
      PARTITION BY enquiry__c
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_competitors_considered__c`
)
SELECT
  enquiry__c as opportunity_id,
  make__c as competitor_product_interested,
  model__c as competitor_variant_interested,
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_master_booking 
AS
WITH ranked_leads AS (
  SELECT
    opportunity__c,
    booking_amount__c,
    booking_date__c,
    customer_expected_delivery_date__c,
    selling_price__c,
    model_description__c,
    pvariant__c,
    ROW_NUMBER() OVER (
      PARTITION BY opportunity__c
      ORDER BY lastmodifieddate DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.sfdc_ace_booking__c`
)
SELECT
  opportunity__c as opportunity_id,
  booking_amount__c as booking_amount,
  booking_date__c as booking_date,
  customer_expected_delivery_date__c as booking_expected_delivery_date,
  selling_price__c as booking_selling_price,
  model_description__c as booking_model_purchased,
  pvariant__c as booking_model_variant
FROM ranked_leads
WHERE rn = 1

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp 
AS
SELECT c.*, o.* EXCEPT(contact_id)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_master_opportunity` AS o
ON
  c.contact_id = o.contact_id

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td 
AS
SELECT c.*, o.* EXCEPT(opportunity_id)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_master_test_drive` AS o
ON
  c.opportunity_id = o.opportunity_id

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task 
AS
SELECT c.*, o.* EXCEPT(opportunity_id)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_master_task` AS o
ON
  c.opportunity_id = o.opportunity_id

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp 
AS
SELECT c.*, o.* EXCEPT(opportunity_id)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_master_competitors` AS o
ON
  c.opportunity_id = o.opportunity_id

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp_book 
AS
SELECT c.*, o.* EXCEPT(opportunity_id)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.testmay.customer_master_booking` AS o
ON
  c.opportunity_id = o.opportunity_id

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp_book_enquiry_survey 
AS
SELECT c.*, o.* EXCEPT(enquiry_number)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp_book` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_enquiry_survey` AS o
ON
  c.enquiry_number = o.enquiry_number

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp_book_enquiry_survey_td_survey 
AS
SELECT c.*, o.* EXCEPT(enquiry_number)
FROM
  `<<PROJECT_ID>>.<<DATASET_ID>>.contact_lead_opp_td_task_comp_book_enquiry_survey` AS c
LEFT JOIN
  `<<PROJECT_ID>>.<<DATASET_ID>>.customer_testdrive_survey` AS o
ON
  c.enquiry_number = o.enquiry_number

CREATE OR REPLACE VIEW <<PROJECT_ID>>.<<DATASET_ID>>.customer_enquiry_survey
AS
WITH ranked_leads AS (
  SELECT
  enquiry_number,
  enquiry_overall_experience,
  exp_didnot_meet_expectations,
    ROW_NUMBER() OVER (
      PARTITION BY enquiry_number
      ORDER BY recorded_date DESC
    ) AS rn
  FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.intello_enquiry_survey`
)
SELECT
  enquiry_number,
  enquiry_overall_experience as enquiry_experience,
  exp_didnot_meet_expectations as enquiry_feeback,
FROM ranked_leads
WHERE rn = 1


## This needs to be scheduled as per inputs from MDP Team in asia-south1 region.  
DROP TABLE IF EXISTS
  <<PROJECT_ID>>.<<DATASET_ID>>.customer_final;

CREATE TABLE <<PROJECT_ID>>.<<DATASET_ID>>.customer_final
CLUSTER BY
(mobilephone)  
AS 
SELECT c.* EXCEPT(contact_id, opportunity_id, enquiry_number)
FROM `<<MDP_PROJECT_ID>>.<<MDP_DATASET_ID>>.contact_lead_opp_td_task_comp_book_enquiry_survey_td_survey` AS c
