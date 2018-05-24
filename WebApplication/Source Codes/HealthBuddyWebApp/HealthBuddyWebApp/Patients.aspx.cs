using System;
using System.Drawing.Printing;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Runtime;
using System.Data;
using System.Web.UI.WebControls;
using System.Drawing;

namespace HealthBuddyWebApp
{
    public partial class Patients : System.Web.UI.Page
    {
        DataTable dt = new DataTable();
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        //End 

        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Patients";
            if (!IsPostBack)
            {
                DataTable dt = ScanRequest();
                Session["Sort"] = "Patient ID ASC";
                dt.DefaultView.Sort = "Patient ID ASC";
                BindGridView(dt);
                Session["DataTable"] = dt;
                lb_All.ForeColor = Color.Black;
                lb_All.Enabled = false;
                pnl_AllPatients.Visible = true;
                Session["Panel"] = "All";
            }
        }
        public void BindGridView(DataTable dt)
        {
            gv_Patients.DataSource = dt;
            gv_Patients.DataBind();
        }
        public DataTable ScanRequest()
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID, patientname, phoneNumber, DeviceID"
            };

            var response = client.Scan(request);
            DataColumn patientIDColumn = dt.Columns.Add("Patient ID");
            patientIDColumn.ReadOnly = true;
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Phone Number"));
            dt.Columns.Add(new DataColumn("Ward Number"));
            dt.Columns.Add(new DataColumn("Bed Number"));

            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                int idx = 0;
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("phoneNumber"))
                    {
                        attributeName = "Phone Number";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("patientname"))
                    {
                        attributeName = "Patient Name";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Patient ID";
                        newPatientRow[attributeName] = value.N;
                        idx++;
                    }
                    if (attributeName.Equals("DeviceID"))
                    {
                        string deviceID = value.S;
                        var request2 = new ScanRequest
                        {
                            TableName = "Devices",
                            ProjectionExpression = "bedNo, wardNo",
                            FilterExpression = "deviceID = :val",
                            ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":val", new AttributeValue { S = deviceID }}
                            }
                        };
                        var response2 = client.Scan(request2);
                        foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response2.Items)
                        {
                            foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                            {
                                string attributeName2 = kvp2.Key;
                                AttributeValue value2 = kvp2.Value;
                                if (attributeName2.Equals("wardNo"))
                                {
                                    attributeName = "Ward Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                                if (attributeName2.Equals("bedNo"))
                                {
                                    attributeName = "Bed Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                            }
                        }
                    }
                    //Label1.Text += attributeName + ": " + "<br>" +
                    //    (value.S == null ? "" : value.S) + "" +
                    //    (value.N == null ? "" : value.N) + "<br>";
                }
                dt.Rows.Add(newPatientRow);
                //Label1.Text += "************************************************<br>";
            }
            return dt;
        }

        protected void ddl_Sort_SelectedIndexChanged(object sender, EventArgs e)
        {
            string sortBy = ddl_Sort.SelectedValue;
            Session["Sort"] = sortBy;
            DataTable dt = (DataTable)Session["DataTable"];
            dt.DefaultView.Sort = sortBy;
            gv_Patients.DataSource = dt;
            gv_Patients.DataBind();
        }

        public void updateItem(string patientID, Dictionary<string, AttributeValue> ExpressionAttributeValues)
        {
            var request = new UpdateItemRequest
            {
                TableName = "Patients",
                Key = new Dictionary<string, AttributeValue>() { { "RoundingID", new AttributeValue { N = patientID } } },
                ExpressionAttributeNames = new Dictionary<string, string>()
                {
                    {"#N", "patientname"},
                    {"#P", "phoneNumber"},
                    {"#D", "DeviceID" },
                    {"#U", "inUse"  }
                },
                ExpressionAttributeValues = ExpressionAttributeValues,
                // This expression does the following:
                // 1) Change Name
                // 2) Change Phone
                UpdateExpression = "SET #N = :name, #P = :phone, #D = :deviceID, #U = :inUse"
            };
            var response = client.UpdateItem(request);
        }

        protected void gv_Patients_RowEditing(object sender, GridViewEditEventArgs e)
        {
            //Set the edit index.
            gv_Patients.EditIndex = e.NewEditIndex;
            int idx = e.NewEditIndex;
            DataTable dt = (DataTable)Session["DataTable"];
            //Bind data to the GridView control.
            BindGridView(dt);
            LinkButton btn = gv_Patients.Rows[idx].FindControl("lb_Update2") as LinkButton;
            TextBox tb1 = (TextBox)(gv_Patients.Rows[idx].Cells[4].Controls[0]);
            TextBox tb2 = (TextBox)(gv_Patients.Rows[idx].Cells[5].Controls[0]);
        }

        protected void gv_Patients_RowUpdating(object sender, GridViewUpdateEventArgs e)
        {
           
            int number;
            DataTable dt = (DataTable)Session["DataTable"];
            //Get the Patient ID
            GridViewRow row = gv_Patients.Rows[e.RowIndex];
            int id = Convert.ToInt32(row.Cells[1].Text);
            string PatientID = id.ToString();
            //Basically,
            //Patient Name = ((TextBox)(row.Cells[2].Controls[0])).Text;
            //Phone Number = ((TextBox)(row.Cells[3].Controls[0])).Text;
            //Ward No = ((TextBox)(row.Cells[4].Controls[0])).Text;
            //Bed No = ((TextBox)(row.Cells[5].Controls[0])).Text;
            string PatientName = ((TextBox)(row.Cells[2].Controls[0])).Text;
            string PatientPhone = ((TextBox)(row.Cells[3].Controls[0])).Text;
            string WardNo = ((TextBox)(row.Cells[4].Controls[0])).Text;
            string BedNo = ((TextBox)(row.Cells[5].Controls[0])).Text;
            //Check if Phone is Numerical
            bool phoneVerify = Int32.TryParse(PatientPhone, out number);
            //Check if Device Exists (By Getting Count)
            int deviceExists = getDeviceID(BedNo, WardNo);
            //Then Get Device ID
            string DeviceID = getDeviceID2(BedNo, WardNo);
            //Will Return False if there is a Patient already logged in to the device
            bool patientInUse = has_inUsePatient(DeviceID);
            int inUseId = get_inUsePatientID(DeviceID);

            bool numberClear = number_clear(PatientPhone);

            if (PatientPhone.Length == 8 && phoneVerify && deviceExists > 0 && !DeviceID.Equals("Error") && numberClear)
            {   
                if (Session["Panel"].ToString().Equals("All") && id != inUseId)
                {
                    //btn.OnClientClick = "return confirm('There is already a user signed in to ward " + WardNo + " and bed " + BedNo + ". Clicking Confirm will sign this user out.')";
                    //Create the Dictionary to Pass on to the update method
                    Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                    {
                        {":name",new AttributeValue { S = PatientName }},
                        {":phone",new AttributeValue { S = PatientPhone }},
                        {":deviceID",new AttributeValue { S = DeviceID }},
                        {":inUse",new AttributeValue { N = "0" }}
                    };

                        //Call the Update Method
                        updateItem(PatientID, expressionpatient);

                        //Bind the New Results 
                        dt = ScanRequest();
                }
                else if (Session["Panel"].ToString().Equals("All") && !patientInUse && id==inUseId )
                {
                    //Create the Dictionary to Pass on to the update method
                    Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                    {
                        {":name",new AttributeValue { S = PatientName }},
                        {":phone",new AttributeValue { S = PatientPhone }},
                        {":deviceID",new AttributeValue { S = DeviceID }},
                        {":inUse",new AttributeValue { N = "1" }}
                    };

                    //Call the Update Method
                    updateItem(PatientID, expressionpatient);

                    //Bind the New Results 
                    dt = ScanRequest();
                }
                else if (Session["Panel"].ToString().Equals("Active") && patientInUse && id == inUseId)
                {
                    //Create the Dictionary to Pass on to the update method
                    Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                    {
                        {":name",new AttributeValue { S = PatientName }},
                        {":phone",new AttributeValue { S = PatientPhone }},
                        {":deviceID",new AttributeValue { S = DeviceID }},
                        {":inUse",new AttributeValue { N = "1" }}
                    };

                    //Call the Update Method
                    updateItem(PatientID, expressionpatient);

                    //Bind the New Results 
                    dt = ScanRequest2();
                }
                else if (Session["Panel"].ToString().Equals("Active") && id!=inUseId)
                {
                   
                    //btn.OnClientClick = "return confirm('There is already a user signed in to ward "+WardNo +" and bed "+BedNo +". Clicking Confirm will sign this user out.')";
                    //Create the Dictionary to Pass on to the update method
                    Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                    {
                        {":name",new AttributeValue { S = PatientName }},
                        {":phone",new AttributeValue { S = PatientPhone }},
                        {":deviceID",new AttributeValue { S = DeviceID }},
                        {":inUse",new AttributeValue { N = "0" }}
                    };

                    //Call the Update Method
                    updateItem(PatientID, expressionpatient);
                    //Bind the New Results 
                    dt = ScanRequest2();
                }

                Session["DataTable"] = dt;
                dt.DefaultView.Sort = Session["Sort"].ToString();

                //Reset the edit index.
                gv_Patients.EditIndex = -1;

                //Bind data to the GridView control.
                BindGridView(dt);
                lbl_Error.Visible = true;
                lbl_Error.ForeColor = System.Drawing.ColorTranslator.FromHtml("#4BB543");
                lbl_Error.Text = "Update Success";
            }
            else if (!phoneVerify)
            {
                lbl_Error.Visible = true;
                lbl_Error.Text += "Phone Number is not a number! <br/>";
            }
            else if (!numberClear)
            {
                lbl_Error.Visible = true;
                lbl_Error.Text += "Phone Number Already in Use! <br/>";
            }
            else if (!PatientPhone.Length.Equals(8))
            {
                lbl_Error.Visible = true;
                lbl_Error.Text += "Phone Number must be 8 Digits. <br/>";
            }
            else if (deviceExists < 1 || DeviceID.Equals("Error"))
            {
                lbl_Error.Visible = true;
                lbl_Error.Text += "No Device Configured in Ward " + WardNo + ", Bed " + BedNo + ". Please Configure your device <a href='../Devices.aspx' Title='Click Me'><span>Here</span></a><br/>";
            }

        }
        protected void gv_Patients_RowCancelingEdit(object sender, GridViewCancelEditEventArgs e)
        {
            //Reset the edit index.
            gv_Patients.EditIndex = -1;
            DataTable dt = (DataTable)Session["DataTable"];
            //Bind data to the GridView control.
            BindGridView(dt);
        }

        protected int getDeviceID(string bedNo, string WardNo)
        {
            var request = new ScanRequest
            {
                TableName = "Devices",
                ProjectionExpression = "deviceID",
                FilterExpression = "bedNo = :bed and wardNo = :ward",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":bed", new AttributeValue { S = bedNo }},
                                {":ward", new AttributeValue { S = WardNo }}
                            }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            return count;
        }

        protected string getDeviceID2(string bedNo, string WardNo)
        {
            var request = new ScanRequest
            {
                TableName = "Devices",
                ProjectionExpression = "deviceID",
                FilterExpression = "bedNo = :bed and wardNo = :ward",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":bed", new AttributeValue { S = bedNo }},
                                {":ward", new AttributeValue { S = WardNo }}
                            }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count == 1)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        return value.S.ToString();
                    }
                }
            }
            else
            {
                return "Error";
            }
            return "Error";
        }

        //Link Buttons
        protected void lb_All_Click(object sender, EventArgs e)
        {
            pnl_AllPatients.Visible = true;

            lb_All.ForeColor = Color.Black;
            lb_All.Enabled = false;

            lb_Active.ForeColor = default(Color);
            lb_Active.Enabled = true;

            Session["Panel"] = "All";
            DataTable dt = ScanRequest();
            Session["DataTable"] = dt;
            BindGridView(dt);
        }

        protected void lb_Active_Click(object sender, EventArgs e)
        {
            pnl_AllPatients.Visible = true;

            lb_Active.ForeColor = Color.Black;
            lb_Active.Enabled = false;

            lb_All.ForeColor = default(Color);
            lb_All.Enabled = true;

            Session["Panel"] = "Active";
            DataTable dt = ScanRequest2();
            Session["DataTable"] = dt;
            BindGridView(dt);

        }

        protected void gv_Patients_SelectedIndexChanged(object sender, EventArgs e)
        {
            //Get the Patient ID
            string PatientID = gv_Patients.SelectedRow.Cells[1].Text;
            Session["PatientID"] = PatientID;
            Response.Redirect("~/Roundings.aspx");
        }

        protected void gv_Patients_RowDeleting(object sender, GridViewDeleteEventArgs e)
        {
            DataTable dt = (DataTable)Session["DataTable"];
            //Get the Patient ID
            GridViewRow row = gv_Patients.Rows[e.RowIndex];
            int id = Convert.ToInt32(row.Cells[1].Text);
            string PatientID = id.ToString();

            //Delete
            delete_patient(PatientID);

            //Bind the New Results 
            dt = ScanRequest();
            Session["DataTable"] = dt;
            dt.DefaultView.Sort = Session["Sort"].ToString();

            //Reset the edit index.
            gv_Patients.EditIndex = -1;

            //Bind data to the GridView control.
            BindGridView(dt);
            lbl_Error.Visible = true;
            lbl_Error.ForeColor = System.Drawing.ColorTranslator.FromHtml("#4BB543");
            lbl_Error.Text = "Update Success";       
        }

        protected void delete_patient(string patientID)
        {
            string tableName = "Patients";

            var request = new DeleteItemRequest
            {
                TableName = tableName,
                Key = new Dictionary<string, AttributeValue>() {
                    { "RoundingID", new AttributeValue { N = patientID } } },
            };

            var response = client.DeleteItem(request);
        }

        public DataTable ScanRequest2()
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID, patientname, phoneNumber, DeviceID, inUse",
                FilterExpression = "inUse = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { N = "1" }}
                }
            };

            var response = client.Scan(request);
            DataColumn patientIDColumn = dt.Columns.Add("Patient ID");
            patientIDColumn.ReadOnly = true;
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Phone Number"));
            dt.Columns.Add(new DataColumn("Ward Number"));
            dt.Columns.Add(new DataColumn("Bed Number"));

            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                int idx = 0;
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("phoneNumber"))
                    {
                        attributeName = "Phone Number";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("patientname"))
                    {
                        attributeName = "Patient Name";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Patient ID";
                        newPatientRow[attributeName] = value.N;
                        idx++;
                    }
                    if (attributeName.Equals("DeviceID"))
                    {
                        string deviceID = value.S;
                        var request2 = new ScanRequest
                        {
                            TableName = "Devices",
                            ProjectionExpression = "bedNo, wardNo",
                            FilterExpression = "deviceID = :val",
                            ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":val", new AttributeValue { S = deviceID }}
                            }
                        };
                        var response2 = client.Scan(request2);
                        foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response2.Items)
                        {
                            foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                            {
                                string attributeName2 = kvp2.Key;
                                AttributeValue value2 = kvp2.Value;
                                if (attributeName2.Equals("wardNo"))
                                {
                                    attributeName = "Ward Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                                if (attributeName2.Equals("bedNo"))
                                {
                                    attributeName = "Bed Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                            }
                        }
                    }
                    //Label1.Text += attributeName + ": " + "<br>" +
                    //    (value.S == null ? "" : value.S) + "" +
                    //    (value.N == null ? "" : value.N) + "<br>";
                }
                dt.Rows.Add(newPatientRow);
                //Label1.Text += "************************************************<br>";
            }
            return dt;
        }

        public void BindGridView2(DataTable dt)
        {
            gv_Patients.DataSource = dt;
            gv_Patients.DataBind();
        }
        protected bool has_inUsePatient(string deviceID)
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                FilterExpression = "inUse = :inUse and DeviceID = :deviceID",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":inUse", new AttributeValue { N = "1" }},
                    {":deviceID", new AttributeValue { S = deviceID }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count == 0)
            {
                return true;
            }
            else if (count > 0)
            {
                return false;
            }
            return false;
        }
        protected int get_inUsePatientID(string deviceID)
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                FilterExpression = "inUse = :inUse and DeviceID = :deviceID",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":inUse", new AttributeValue { N = "1" }},
                    {":deviceID", new AttributeValue { S = deviceID }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count == 0)
            {
                return 0;
            }
            else if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                    {
                        string attributeName = kvp2.Key;
                        AttributeValue value = kvp2.Value;
                        if (attributeName == "RoundingID")
                        {
                            return Convert.ToInt32(value.N);
                        }    
                    }
                }
            }
            return 0;
        }
        protected void gv_Patients_RowDataBound(object sender, GridViewRowEventArgs e)
        {
            if (e.Row.RowType == DataControlRowType.DataRow)
            {
                if ((e.Row.RowState & DataControlRowState.Edit) > 0)
                {
                    LinkButton linkbutton = (LinkButton)e.Row.FindControl("lb_Update2");
                    string bed = ((TextBox)(e.Row.Cells[5].Controls[0])).Text;
                    string ward = ((TextBox)(e.Row.Cells[4].Controls[0])).Text;
                    int id = Convert.ToInt32(e.Row.Cells[1].Text);
                    string DeviceID = getDeviceID2(bed, ward);
                    int inUseId = get_inUsePatientID(DeviceID);
                    //Will Return False if there is a Patient already logged in to the device
                    bool patientInUse = has_inUsePatient(DeviceID);
                    if (!patientInUse && id != inUseId)
                    {
                        linkbutton.OnClientClick = "return confirm('There is already a user signed in to Ward " + ward + " and Bed " + bed + ". Clicking OK will sign this user out.')";
                    }
                    

                }
            }
        }

        protected void lb_Add_Click(object sender, EventArgs e)
        {
            Response.Redirect("~/AddPatient.aspx");
        }

        protected bool number_clear(string number)
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID",
                FilterExpression = "phoneNumber = :val",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                    {":val", new AttributeValue { S = number }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count > 0)
            {
                return false;
            }
            else if (count == 0)
            {
                return true;
            }
            return false;
        }
    }
}