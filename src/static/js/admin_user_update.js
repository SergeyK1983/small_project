"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* ==========================================
         * API
         * ========================================== */

        const GET_USER_API_URL =
            "/auth/v1/adm-user";


        const UPDATE_USER_API_URL =
            "/auth/v1/adm-update-user";


        /* ==========================================
         * User ID
         * ========================================== */

        const params =
            new URLSearchParams(
                window.location.search
            );


        const userId =
            params.get(
                "user_id"
            );


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


        const userContent =
            document.getElementById(
                "user-content"
            );


        const errorMessage =
            document.getElementById(
                "error-message"
            );


        const retryButton =
            document.getElementById(
                "retry-button"
            );


        const userDescription =
            document.getElementById(
                "user-description"
            );


        /* ==========================================
         * User information
         * ========================================== */

        const userIdElement =
            document.getElementById(
                "user-id"
            );


        const userUsername =
            document.getElementById(
                "user-username"
            );


        const userEmail =
            document.getElementById(
                "user-email"
            );


        const userFullName =
            document.getElementById(
                "user-full-name"
            );


        const userFirstName =
            document.getElementById(
                "user-first-name"
            );


        const userSecondName =
            document.getElementById(
                "user-second-name"
            );


        const userLastName =
            document.getElementById(
                "user-last-name"
            );


        /* ==========================================
         * Admin fields
         * ========================================== */

        const isActive =
            document.getElementById(
                "is-active"
            );


        const isStaff =
            document.getElementById(
                "is-staff"
            );


        const isSuperuser =
            document.getElementById(
                "is-superuser"
            );


        /* ==========================================
         * Form
         * ========================================== */

        const adminUserForm =
            document.getElementById(
                "admin-user-form"
            );


        const saveButton =
            document.getElementById(
                "save-button"
            );


        /* ==========================================
         * Success
         * ========================================== */

        const successState =
            document.getElementById(
                "success-state"
            );


        const successMessage =
            document.getElementById(
                "success-message"
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


            userContent.hidden =
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
                Array.isArray(
                    data.detail
                )
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
         * Render user
         * ========================================== */

        function renderUser(
            user
        ) {

            /*
             * Общая информация
             */

            userIdElement.textContent =
                user.id ?? "—";


            userUsername.textContent =
                user.username ?? "—";


            userEmail.textContent =
                user.email ?? "—";


            userFullName.textContent =
                user.full_name || "—";


            userFirstName.textContent =
                user.first_name || "—";


            userSecondName.textContent =
                user.second_name || "—";


            userLastName.textContent =
                user.last_name || "—";


            /*
             * Заголовок
             */

            userDescription.textContent =
                `Изменение пользователя: ${user.username}`;


            /*
             * Административные поля
             *
             * Теперь мы получаем
             * реальные значения
             * с backend.
             */

            isActive.checked =
                Boolean(
                    user.is_active
                );


            isStaff.checked =
                Boolean(
                    user.is_staff
                );


            isSuperuser.checked =
                Boolean(
                    user.is_superuser
                );

        }


        /* ==========================================
         * Load user
         * ========================================== */

        async function loadUser() {

            showState(
                "loading"
            );


            successState.hidden =
                true;


            /*
             * Проверяем наличие ID
             */

            if (!userId) {

                errorMessage.textContent =
                    "Не указан идентификатор пользователя.";


                showState(
                    "error"
                );


                return;
            }


            try {

                const userUrl =
                    `${GET_USER_API_URL}/${encodeURIComponent(userId)}`;


                const response =
                    await fetch(
                        userUrl,
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
                 * Пользователь не авторизован
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
                 * Нет прав администратора
                 */

                if (
                    response.status ===
                    403
                ) {

                    errorMessage.textContent =
                        "У вас нет прав для просмотра данных пользователя.";


                    showState(
                        "error"
                    );


                    return;
                }


                const data =
                    await response.json();


                /*
                 * Любая другая ошибка
                 */

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
                 * Отображаем пользователя
                 */

                renderUser(
                    data
                );


                showState(
                    "content"
                );


            } catch (error) {

                console.error(
                    "Load user error:",
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
         * Update user
         * ========================================== */

        async function updateUser() {

            /*
             * Формируем JSON
             *
             * UserAdminUpdateSchema:
             *
             * {
             *     is_active: bool | None,
             *     is_staff: bool | None,
             *     is_superuser: bool | None
             * }
             */

            const updateData = {

                is_active:
                    isActive.checked,

                is_staff:
                    isStaff.checked,

                is_superuser:
                    isSuperuser.checked

            };


            const updateUrl =
                `${UPDATE_USER_API_URL}/${encodeURIComponent(userId)}`;


            const response =
                await fetch(
                    updateUrl,
                    {
                        method:
                            "PATCH",

                        headers: {

                            "Accept":
                                "application/json",

                            "Content-Type":
                                "application/json"

                        },

                        credentials:
                            "same-origin",

                        body:
                            JSON.stringify(
                                updateData
                            )
                    }
                );


            /*
             * Сессия закончилась
             */

            if (
                response.status ===
                401
            ) {

                window.location.href =
                    "/dev";


                return null;

            }


            let data =
                null;


            try {

                data =
                    await response.json();

            } catch (error) {

                console.error(
                    "Invalid update response:",
                    error
                );

            }


            if (
                !response.ok
            ) {

                throw new Error(
                    getApiErrorMessage(
                        data
                    )
                );

            }


            return data;

        }


        /* ==========================================
         * Submit
         * ========================================== */

        adminUserForm.addEventListener(
            "submit",
            async (
                event
            ) => {

                event.preventDefault();


                successState.hidden =
                    true;


                saveButton.disabled =
                    true;


                saveButton.textContent =
                    "Сохранение...";


                try {

                    const data =
                        await updateUser();


                    /*
                     * При 401
                     * updateUser уже
                     * сделал redirect.
                     */

                    if (!data) {

                        return;

                    }


                    /*
                     * Показываем успешное
                     * обновление.
                     */

                    successMessage.textContent =
                        `Данные пользователя "${data.username}" успешно обновлены.`;


                    successState.hidden =
                        false;


                    /*
                     * Обновляем отображаемые
                     * административные значения.
                     *
                     * Backend возвращает UserBase.
                     */

                    renderUser(
                        data
                    );


                } catch (error) {

                    console.error(
                        "Update user error:",
                        error
                    );


                    errorMessage.textContent =
                        error.message ||
                        "Не удалось изменить данные пользователя.";


                    /*
                     * Показываем ошибку.
                     */

                    errorState.hidden =
                        false;

                } finally {

                    saveButton.disabled =
                        false;


                    saveButton.textContent =
                        "Сохранить изменения";

                }

            }
        );


        /* ==========================================
         * Retry
         * ========================================== */

        retryButton.addEventListener(
            "click",
            () => {

                loadUser();

            }
        );


        /* ==========================================
         * Initial load
         * ========================================== */

        loadUser();

    }
);