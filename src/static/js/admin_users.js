"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* ==========================================
         * API
         * ========================================== */

        const USERS_API_URL =
            "/auth/v1/users";


        /* ==========================================
         * Page URLs
         * ========================================== */

        const UPDATE_USER_PAGE_URL =
            "/dev/admin/user/update";

        const USER_ACCOUNTS_PAGE_URL =
            "/dev/admin/user/accounts";


        /* ==========================================
         * DOM
         * ========================================== */

        const loadingState =
            document.getElementById(
                "loading-state"
            );

        const errorState =
            document.getElementById(
                "error-state"
            );

        const usersContent =
            document.getElementById(
                "users-content"
            );

        const errorMessage =
            document.getElementById(
                "error-message"
            );

        const retryButton =
            document.getElementById(
                "retry-button"
            );

        const usersTableBody =
            document.getElementById(
                "users-table-body"
            );

        const usersCountMessage =
            document.getElementById(
                "users-count-message"
            );


        /* ==========================================
         * Page state
         * ========================================== */

        function showState(
            state
        ) {

            loadingState.hidden =
                state !== "loading";

            errorState.hidden =
                state !== "error";

            usersContent.hidden =
                state !== "content";
        }


        /* ==========================================
         * API error
         * ========================================== */

        function getApiErrorMessage(
            data
        ) {

            if (!data) {

                return (
                    "Произошла неизвестная ошибка."
                );
            }


            if (
                typeof data.detail ===
                "string"
            ) {

                return data.detail;
            }


            if (
                Array.isArray(data.detail)
            ) {

                return data.detail
                    .map(
                        error =>
                            error.msg ||
                            "Ошибка валидации."
                    )
                    .join(" ");
            }


            if (
                typeof data.message ===
                "string"
            ) {

                return data.message;
            }


            return (
                "Произошла ошибка. " +
                "Попробуйте еще раз."
            );
        }


        /* ==========================================
         * Load users
         * ========================================== */

        async function loadUsers() {

            showState(
                "loading"
            );


            try {

                const response =
                    await fetch(
                        USERS_API_URL,
                        {
                            method:
                                "GET",

                            headers: {
                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin"
                        }
                    );


                /*
                 * Пользователь не авторизован.
                 */

                if (
                    response.status ===
                    401
                ) {

                    window.location.href =
                        "/dev";

                    return;
                }


                /*
                 * Недостаточно прав.
                 */

                if (
                    response.status ===
                    403
                ) {

                    errorMessage.textContent =
                        "У вас нет прав для просмотра списка пользователей.";

                    showState(
                        "error"
                    );

                    return;
                }


                const data =
                    await response.json();


                if (
                    !response.ok
                ) {

                    errorMessage.textContent =
                        getApiErrorMessage(
                            data
                        );

                    showState(
                        "error"
                    );

                    return;
                }


                /*
                 * Проверяем формат ответа.
                 */

                if (
                    !data ||
                    !Array.isArray(
                        data.users
                    )
                ) {

                    errorMessage.textContent =
                        "Сервер вернул некорректный список пользователей.";

                    showState(
                        "error"
                    );

                    return;
                }


                renderUsers(
                    data.users
                );

                showState(
                    "content"
                );


            } catch (error) {

                console.error(
                    "Load users error:",
                    error
                );


                errorMessage.textContent =
                    "Не удалось подключиться к серверу.";


                showState(
                    "error"
                );
            }
        }


        /* ==========================================
         * Create table cell
         * ========================================== */

        function createCell(
            value,
            className = ""
        ) {

            const cell =
                document.createElement(
                    "td"
                );


            cell.textContent =
                value ?? "—";


            if (
                className
            ) {

                cell.className =
                    className;
            }


            return cell;
        }


        /* ==========================================
         * Create action link
         * ========================================== */

        function createActionLink(
            text,
            url,
            className = "button"
        ) {

            const link =
                document.createElement(
                    "a"
                );


            link.textContent =
                text;


            link.href =
                url;


            link.className =
                className;


            return link;
        }


        /* ==========================================
         * Render users
         * ========================================== */

        function renderUsers(
            users
        ) {

            /*
             * Очищаем старые строки.
             */

            usersTableBody.replaceChildren();


            /*
             * Количество пользователей.
             */

            const usersCount =
                users.length;


            usersCountMessage.textContent =
                `Всего пользователей: ${usersCount}`;


            /*
             * Пустой список.
             */

            if (
                usersCount === 0
            ) {

                const row =
                    document.createElement(
                        "tr"
                    );


                const cell =
                    document.createElement(
                        "td"
                    );


                cell.colSpan =
                    7;


                cell.className =
                    "empty-users";


                cell.textContent =
                    "Пользователи отсутствуют.";


                row.appendChild(
                    cell
                );


                usersTableBody.appendChild(
                    row
                );


                return;
            }


            /*
             * Формируем строки.
             */

            users.forEach(
                user => {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    /*
                     * ID
                     */

                    row.appendChild(
                        createCell(
                            user.id,
                            "user-id-cell"
                        )
                    );


                    /*
                     * Username
                     */

                    row.appendChild(
                        createCell(
                            user.username
                        )
                    );


                    /*
                     * Email
                     */

                    row.appendChild(
                        createCell(
                            user.email
                        )
                    );


                    /*
                     * First name
                     */

                    row.appendChild(
                        createCell(
                            user.first_name
                        )
                    );


                    /*
                     * Second name
                     */

                    row.appendChild(
                        createCell(
                            user.second_name
                        )
                    );


                    /*
                     * Last name
                     */

                    row.appendChild(
                        createCell(
                            user.last_name
                        )
                    );


                    /*
                     * Actions
                     */

                    const actionsCell =
                        document.createElement(
                            "td"
                        );


                    const actions =
                        document.createElement(
                            "div"
                        );


                    actions.className =
                        "user-actions";


                    /*
                     * Update
                     */

                    const updateUrl =
                        new URL(
                            UPDATE_USER_PAGE_URL,
                            window.location.origin
                        );


                    updateUrl.searchParams.set(
                        "user_id",
                        user.id
                    );


                    const updateLink =
                        createActionLink(
                            "Изменить пользователя",
                            updateUrl.toString()
                        );


                    actions.appendChild(
                        updateLink
                    );


                    /*
                     * Accounts
                     */

                    const accountsUrl =
                        new URL(
                            USER_ACCOUNTS_PAGE_URL,
                            window.location.origin
                        );


                    accountsUrl.searchParams.set(
                        "user_id",
                        user.id
                    );


                    const accountsLink =
                        createActionLink(
                            "Счета и балансы",
                            accountsUrl.toString()
                        );


                    actions.appendChild(
                        accountsLink
                    );


                    /*
                     * Delete
                     */

                    const deleteButton =
                        document.createElement(
                            "button"
                        );


                    deleteButton.type =
                        "button";


                    deleteButton.className =
                        "button button-danger";


                    deleteButton.textContent =
                        "Удалить пользователя";


                    deleteButton.dataset.userId =
                        user.id;


                    deleteButton.dataset.username =
                        user.username;


                    deleteButton.addEventListener(
                        "click",
                        () => {

                            deleteUser(
                                user.id,
                                user.username,
                                deleteButton
                            );

                        }
                    );


                    actions.appendChild(
                        deleteButton
                    );


                    actionsCell.appendChild(
                        actions
                    );


                    row.appendChild(
                        actionsCell
                    );


                    usersTableBody.appendChild(
                        row
                    );

                }
            );
        }


        /* ==========================================
         * Delete user
         * ========================================== */

        async function deleteUser(
            userId,
            username,
            button
        ) {

            const confirmed =
                window.confirm(
                    `Вы действительно хотите удалить пользователя "${username}"?`
                );


            if (
                !confirmed
            ) {

                return;
            }


            button.disabled =
                true;


            button.textContent =
                "Удаление...";


            try {

                /*
                 * ВАЖНО:
                 *
                 * Здесь нужно указать реальный
                 * backend URL удаления пользователя
                 * администратором.
                 *
                 * Пока используем предполагаемый:
                 *
                 * DELETE /auth/v1/delete-user/{user_id}
                 */

                const deleteUrl = `/auth/v1/adm-delete-user/${encodeURIComponent(userId)}`;


                const response =
                    await fetch(
                        deleteUrl,
                        {
                            method:
                                "DELETE",

                            headers: {
                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin"
                        }
                    );


                if (
                    response.status ===
                    401
                ) {

                    window.location.href =
                        "/dev";

                    return;
                }


                if (
                    response.status ===
                    403
                ) {

                    window.alert(
                        "У вас нет прав для удаления пользователя."
                    );

                    return;
                }


                let data =
                    null;


                try {

                    data =
                        await response.json();

                } catch (
                    error
                ) {

                    console.error(
                        "Invalid delete response:",
                        error
                    );
                }


                if (
                    !response.ok
                ) {

                    window.alert(
                        getApiErrorMessage(
                            data
                        )
                    );

                    return;
                }


                /* После успешного удаления заново загружаем список. */
                await loadUsers();

            } catch (error) {
                console.error("Delete user error:", error);
                window.alert("Не удалось удалить пользователя.");

            } finally {
                button.disabled = false;
                button.textContent = "Удалить пользователя";
            }
        }

        /* Retry */
        retryButton.addEventListener("click", () => {
            loadUsers();
        });

        /* Initial load */
        loadUsers();
    }
);