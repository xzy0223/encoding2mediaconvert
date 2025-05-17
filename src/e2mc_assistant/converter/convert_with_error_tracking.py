    def convert(self, source_file: str, template_file: str = None) -> Dict:
        """Execute configuration conversion"""
        # Parse source file
        if source_file.endswith('.xml'):
            source_data = self.parse_xml(source_file)
        else:
            with open(source_file, 'r') as f:
                source_data = json.load(f)
        
        # Load target template (if provided)
        if template_file:
            with open(template_file, 'r') as f:
                target_data = json.load(f)
        else:
            target_data = {"Settings": {"OutputGroups": [{}], "Inputs": [{}]}}
        
        # Track which parameters have been processed
        processed_params = set()
        
        # Apply mapping rules
        try:
            for rule in self.rules:
                current_rule = rule
                # Handle iteration rules
                if rule['source'].get('type') == 'iteration':
                    self.logger.debug(f"Processing iteration rule for {rule['source']['path']}")
                    try:
                        self._process_iteration_rule(rule, source_data, target_data)
                    except Exception as e:
                        raise RuntimeError(f"Error in iteration rule for {rule['source']['path']}: {str(e)}")
                    processed_params.add(rule['source']['path'])
                    continue
                    
                # Handle dummy rules - just mark as processed without actual conversion
                if rule['source'].get('type') == 'dummy':
                    source_path = rule['source']['path']
                    self.logger.debug(f"Processing dummy rule for {source_path}")
                    processed_params.add(source_path)
                    # Log that the parameter was processed but not added to output
                    self.logger.debug(f"Parameter {source_path} marked as processed (dummy type)")
                    continue
                    
                source_path = rule['source']['path']
                source_type = rule['source'].get('type', 'string')
                source_regex = rule['source'].get('regex')
                
                # Get source value
                try:
                    source_value = self.get_value_by_path(source_data, source_path)
                except Exception as e:
                    raise RuntimeError(f"Error getting value for path '{source_path}': {str(e)}")
                
                self.logger.debug(f"Processing rule for {source_path}, value: {source_value}")
                
                # Add to processed parameters
                processed_params.add(source_path)
                
                # Check condition (if any)
                if 'condition' in rule['source'] and source_value is not None:
                    try:
                        if not self.evaluate_condition(rule['source']['condition'], source_value, source_data):
                            self.logger.debug(f"Skipping rule for {source_path} due to source condition")
                            continue
                    except Exception as e:
                        raise RuntimeError(f"Error evaluating condition for {source_path}: {str(e)}")
                
                # If source value doesn't exist, use default (if provided)
                if source_value is None:
                    if 'default' in rule['source']:
                        source_value = rule['source']['default']
                        self.logger.debug(f"Using default value for {source_path}: {source_value}")
                    else:
                        self.logger.debug(f"Skipping rule for {source_path} (no value and no default)")
                        continue
                
                # Process target mapping (can be single target or multiple targets)
                targets = rule['target'] if isinstance(rule['target'], list) else [rule['target']]
                
                for target_index, target in enumerate(targets):
                    current_target = target
                    target_path = target['path']
                    transform = target.get('transform')
                    
                    # Check target condition (if any)
                    if 'condition' in target:
                        try:
                            if not self.evaluate_condition(target['condition'], source_value, source_data):
                                self.logger.debug(f"Skipping target {target_path} due to target condition")
                                continue
                        except Exception as e:
                            raise RuntimeError(f"Error evaluating target condition for {target_path}: {str(e)}")
                    
                    # Process value transformation
                    if 'value' in target:
                        # Process with regex if specified
                        if source_regex:
                            try:
                                match = re.match(source_regex, str(source_value))
                                if match:
                                    value_template = target['value']
                                    # Replace $1, $2, etc. with match groups
                                    for i, group in enumerate(match.groups(), 1):
                                        value_template = value_template.replace(f'${i}', group)
                                    
                                    # Convert to appropriate type
                                    if value_template.isdigit():
                                        target_value = int(value_template)
                                    elif self._is_float(value_template):
                                        target_value = float(value_template)
                                    else:
                                        target_value = value_template
                                    
                                    self.logger.debug(f"Regex transformed {source_value} to {target_value}")
                                else:
                                    self.logger.debug(f"Regex pattern {source_regex} did not match {source_value}")
                                    continue
                            except Exception as e:
                                raise RuntimeError(f"Error applying regex for {source_path}: {str(e)}")
                        else:
                            target_value = target['value']
                            self.logger.debug(f"Using static value: {target_value}")
                    else:
                        target_value = source_value
                        
                        # Apply transformation function
                        if transform:
                            try:
                                context = {'source_data': source_data, 'target_data': target_data}
                                original_value = target_value
                                target_value = self.apply_transform(target_value, transform, context)
                                self.logger.debug(f"Transformed {original_value} using {transform} to {type(target_value)}")
                            except Exception as e:
                                raise RuntimeError(f"Error applying transform '{transform}' for {source_path}: {str(e)}")
                    
                    # Set target value using the improved nested value setter
                    try:
                        self._set_nested_value(target_data, target_path, target_value)
                        self.logger.debug(f"Mapped {source_path}={source_value} to {target_path}")
                    except Exception as e:
                        raise RuntimeError(f"Error setting value at path '{target_path}': {str(e)}")
            
            # Log unmapped parameters
            try:
                self._log_unmapped_parameters(source_data, processed_params)
            except Exception as e:
                self.logger.warning(f"Error logging unmapped parameters: {str(e)}")
            
            # Remove any _dummy sections from the output
            if '_dummy' in target_data:
                del target_data['_dummy']
                self.logger.debug("Removed _dummy section from output")
            
            return target_data
            
        except Exception as e:
            # Add context to the exception
            if 'current_rule' in locals():
                raise RuntimeError(f"Error processing rule for {current_rule.get('source', {}).get('path', 'unknown')}: {str(e)}")
            else:
                raise RuntimeError(f"Error during conversion: {str(e)}")
