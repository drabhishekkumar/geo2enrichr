
/* Abstracts issues of adding new required fields depending on metadata. 95%
 * of this module is only required for a 2015 Coursera MOOC and could be
 * refactored once the course is over.
 *
 * https://www.coursera.org/course/bd2klincs
 */
var Tagger = function(events, templater) {

    var selectedTags = [],
        newFields = [],
        $table;

    var tagsToFields = {
        AGING_BD2K_LINCS_DCIC_COURSERA: {
            young: {
                required: true,
                description: "Age of the young sample"
            },
            old: {
                required: true,
                description: "Age of the old sample"
            },
            age_unit: {
                required: true,
                description: "Unit of age, choose among day, month, year"
            }
        },
        MCF7_BD2K_LINCS_DCIC_COURSERA: {
            pert_type: {
                required: true,
                description: "Perturbation type, choose among genetic, chemical, physical, other"
            },
            pert_name: {
                required: true,
                description: "Perturbagen name"
            },
            pert_id: {
                required: false,
                description: "Identifier of the perturbagen"
            }
        },
        DISEASES_BD2K_LINCS_DCIC_COURSERA: {
            disease_name: {
                required: true,
                description: "Name of the disease"
            },
            disease_id: {
                required: true,
                description: "ID of the disease (from Disease-Ontology or UMLS)"
            }
        },
        LIGANDS_BD2K_LINCS_DCIC_COURSERA: {
            ligand_name: {
                required: true,
                description: "Name of the ligand"
            },
            ligand_id: {
                required: true,
                description: "Identifier of the ligand"
            }
        },
        DRUGS_BD2K_LINCS_DCIC_COURSERA: {
            drug_name: {
                required: true,
                description: "Name of the drug"
            },
            drug_id: {
                required: true,
                description: "ID of the Drug (from DrugBank or PubChem)"
            }
        },
        GENES_BD2K_LINCS_DCIC_COURSERA: {
            pert_type: {
                required: true,
                description: "Perturbation type (KO, KD, OE, Mutation)"
            }
        },
        PATHOGENS_BD2K_LINCS_DCIC_COURSERA: {
            microbe_name: {
                required: true,
                description: "Name of the virus or bacteria"
            },
            microbe_id: {
                required: false,
                description: "Taxonomy ID of the virus or bacteria"
            }
        }
    };

    function addRequiredRows(newTag) {
        $.each(tagsToFields[newTag], function(key, newRow) {
            newFields.push(key);
            var $tr = templater.getTableRow(newRow.description, key);
            $table.append($tr);
        });
    }

    function removeUnrequiredRows(oldTag) {
        $.each(tagsToFields[oldTag], function(key) {
            var $oldRow = $('#' + key),
                idx = newFields.indexOf(key);
            if (idx > -1) {
                newFields.splice(idx, 1);
            }
            $oldRow.remove();
        });
    }

    function watch($input) {
        $input.tagit({
            singleField: true,
            beforeTagAdded: function (evt, ui) {
                var newTag = $(ui.tag).find('.tagit-label').html();
                selectedTags.push(newTag);
                if (typeof tagsToFields[newTag] !== 'undefined') {
                    addRequiredRows(newTag);
                }
            },
            afterTagRemoved: function (evt, ui) {
                var oldTag = $(ui.tag).find('.tagit-label').html(),
                    idx = selectedTags.indexOf(oldTag);
                if (idx > -1) {
                    selectedTags.splice(idx, 1);
                }
                if (typeof tagsToFields[oldTag] !== 'undefined') {
                    removeUnrequiredRows(oldTag);
                }
            }
        });
    }

    function init($input, $t) {
        $table = $t;
        watch($input);
    }

    return {
        init: init,
        getSelectedTags: function() {
            return selectedTags;
        },
        getNewFields: function() {
            return newFields;
        }
    };
};