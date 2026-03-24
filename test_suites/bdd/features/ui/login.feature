Feature: User Authentication
 As a Sauce Demo user
 I want to log in to the application
 So that I can access the inventory

 @smoke
 Scenario: Successful login with the standard user
 Given I am on the login page
 When I enter username "standard_user" and password "secret_sauce"
 And I click the login button
 Then I should be redirected to the inventory page
 And I should see products displayed

 @regression
 Scenario: Successful login with the problem user
 Given I am on the login page
 When I enter username "problem_user" and password "secret_sauce"
 And I click the login button
 Then I should be redirected to the inventory page
 And I should see products displayed

 @regression
 Scenario: Successful login with the performance glitch user
 Given I am on the login page
 When I enter username "performance_glitch_user" and password "secret_sauce"
 And I click the login button
 Then I should be redirected to the inventory page
 And I should see products displayed

 @regression
 Scenario: Successful login with the error user
 Given I am on the login page
 When I enter username "error_user" and password "secret_sauce"
 And I click the login button
 Then I should be redirected to the inventory page
 And I should see products displayed

 @regression
 Scenario: Successful login with the visual user
 Given I am on the login page
 When I enter username "visual_user" and password "secret_sauce"
 And I click the login button
 Then I should be redirected to the inventory page
 And I should see products displayed

 @negative
 Scenario: Failed login with invalid username
 Given I am on the login page
 When I enter username "invalid_user" and password "secret_sauce"
 And I click the login button
 Then I should see an error message "Epic sadface: Username and password do not match any user in this service"
 And I should remain on the login page

 @negative
 Scenario: Failed login with invalid password
 Given I am on the login page
 When I enter username "standard_user" and password "wrong_password"
 And I click the login button
 Then I should see an error message "Epic sadface: Username and password do not match any user in this service"
 And I should remain on the login page

 @negative
 Scenario: Login requires a username
 Given I am on the login page
 When I enter password "secret_sauce" with an empty username
 And I click the login button
 Then I should see an error message "Epic sadface: Username is required"
 And I should remain on the login page

 @edge
 Scenario: Login with locked out user
 Given I am on the login page
 When I enter username "locked_out_user" and password "secret_sauce"
 And I click the login button
 Then I should see an error message "Epic sadface: Sorry, this user has been locked out."
 And I should remain on the login page
