
describe('Is the Censys App Installed', () => {

    it('should find the dashboards', () => {
        // the shell environment variable to set is CYPRESS_SPLUNK_PASSWORD
        const password = Cypress.env('SPLUNK_PASSWORD')
        expect(password, 'password was set').to.be.a('string').and.not.be.empty

        // log in
        cy.visit("http://localhost:8000/");
        cy.url().should('include', 'account/login')
        cy.get('input[id="username"]').type("admin").get('input[id="password"]').type(password)
        cy.get(".loginForm").get(".splButton-primary.btn.btn-primary").first().click()

        // click the Censys app button
        cy.get('a[aria-label="Censys"]').click()

        // click the dashboards link
        cy.get('a[Title="Dashboards"]').click()

        // make sure that the two dashboards we expect are present
        cy.contains("Censys Enterprise")
        cy.contains("Events by type for past day")

        // open the Censys Enterprise Dashboard
        cy.get('a[title="Censys Enterprise"]').click()
        cy.contains("New CVEs for Hosts")

    });


})
