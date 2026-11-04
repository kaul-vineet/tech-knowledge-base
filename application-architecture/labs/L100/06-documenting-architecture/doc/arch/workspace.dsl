workspace "Library Loans" "C4 model of the L100 running example." {

    model {
        member = person "Library member" "Borrows and returns books."
        librarian = person "Librarian" "Looks up and closes loans at the desk."
        email = softwareSystem "E-mail system" "Sends due-date reminders." "External"

        loans = softwareSystem "Library Loans" "Records loans and enforces loan rules." {
            api = container "Loans API" "Layered modular monolith: catalog and loans modules." "Python 3.12, http.server"
            db = container "Loans database" "Stores loans and book status." "SQLite 3" "Database"
        }

        member -> api "Borrows and returns books using" "JSON/HTTP"
        librarian -> api "Looks up loans using" "JSON/HTTP"
        api -> db "Reads from and writes to" "sqlite3"
        api -> email "Sends reminders using" "SMTP"
        email -> member "Sends reminder e-mails to"
    }

    views {
        systemContext loans "SystemContext" {
            include *
            autoLayout
        }

        container loans "Containers" {
            include *
            autoLayout
        }

        styles {
            element "Person" {
                shape Person
            }
            element "Database" {
                shape Cylinder
            }
            element "External" {
                background #999999
            }
        }
    }
}
