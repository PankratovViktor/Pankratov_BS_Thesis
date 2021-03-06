import numpy as np

from . import base

from pyartm.common.timers import SimpleTimer


class Optimizer(base.Optimizer):
    __slots__ = tuple()

    def __init__(
        self,
        regularization_list=None,
        loss_function=None,
        return_counters=False,
        const_phi=False,
        const_theta=False,
        inplace=False,
        verbose=True,
        iteration_callback=None
    ):
        super(Optimizer, self).__init__(
            regularization_list=regularization_list,
            loss_function=loss_function,
            return_counters=return_counters,
            const_phi=const_phi,
            const_theta=const_theta,
            inplace=inplace,
            verbose=verbose,
            iteration_callback=iteration_callback
        )

    def _run(self, n_dw_matrix, docptr, wordptr, phi_matrix, theta_matrix):
        n_tw, n_dt = None, None
        for it in range(self.iters_count):
            with SimpleTimer('iteration'):
                phi_matrix_tr = np.transpose(phi_matrix)

                with SimpleTimer('calc_A_matrix'):
                    A = self.calc_A_matrix(
                        n_dw_matrix, theta_matrix, docptr,
                        phi_matrix_tr, wordptr
                    )

                with SimpleTimer('n_dt'):
                    n_dt = A.dot(phi_matrix_tr) * theta_matrix

                with SimpleTimer('n_tw'):
                    n_tw = np.transpose(
                        A.tocsc().transpose().dot(theta_matrix)
                    ) * phi_matrix

                with SimpleTimer('r_tw, r_dt'):
                    r_tw, r_dt = self.calc_reg_coeffs(
                        it, phi_matrix, theta_matrix, n_tw, n_dt
                    )
                n_tw += r_tw
                n_dt += r_dt

                with SimpleTimer('finish_iteration'):
                    phi_matrix, theta_matrix = self.finish_iteration(
                        it, phi_matrix, theta_matrix, n_tw, n_dt
                    )

        return phi_matrix, theta_matrix, n_tw, n_dt
